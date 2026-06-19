use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);
use File::Path qw(make_path);
use JSON::PP qw(decode_json);

my $repo = $ENV{REPO_ROOT} || '.';

sub script {
    my ($path) = @_;
    return "$repo/$path";
}

sub sq {
    my ($value) = @_;
    $value =~ s/'/'"'"'/g;
    return "'$value'";
}

sub run_cmd {
    my (@parts) = @_;
    my $cmd = join ' ', map { sq($_) } @parts;
    my $out = qx($cmd 2>&1);
    my $exit = $? >> 8;
    return ($exit, $out);
}

sub write_file {
    my ($path, $content) = @_;
    open my $fh, '>:encoding(UTF-8)', $path or die "write $path: $!";
    print {$fh} $content;
}

sub read_file {
    my ($path) = @_;
    open my $fh, '<:encoding(UTF-8)', $path or die "read $path: $!";
    local $/;
    return <$fh>;
}

subtest 'jsonl_validate reports valid, invalid, and missing-key lines' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $file = "$dir/prompts.jsonl";
    write_file(
        $file,
        "{\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}\n" .
        "not-json\n" .
        "{\"prompt\":\"hello\"}\n",
    );

    my ($exit, $out) = run_cmd($^X, script('Perl/data_tools/jsonl_validate.pl'), '--file', $file, '--require', 'messages', '--json');
    my $data = decode_json($out);
    is($exit, 1, 'invalid JSONL exits non-zero');
    is($data->{total_lines}, 3, 'counts total lines');
    is($data->{valid_lines}, 1, 'counts valid lines');
    is($data->{invalid_lines}, 1, 'counts invalid JSON lines');
    is($data->{missing_lines}, 1, 'counts missing required keys');

    write_file($file, "{\"messages\":[]}\n");
    ($exit, $out) = run_cmd($^X, script('Perl/data_tools/jsonl_validate.pl'), '--file', $file, '--require', 'messages');
    is($exit, 0, 'valid JSONL exits zero');
};

subtest 'todo_report finds markers and respects excludes' => sub {
    my $dir = tempdir(CLEANUP => 1);
    make_path("$dir/src", "$dir/.git");
    write_file("$dir/src/app.txt", "TODO: ship this\nplain\nFIXME handle edge\n");
    write_file("$dir/.git/ignored.txt", "TODO: ignore this\n");

    my ($exit, $out) = run_cmd($^X, script('Perl/repo_tools/todo_report.pl'), '--path', $dir, '--format', 'json');
    my $data = decode_json($out);
    is($exit, 0, 'todo report exits zero');
    is($data->{count}, 2, 'finds markers outside excluded dirs');
    like($out, qr/TODO/, 'includes marker');
    unlike($out, qr/ignore this/, 'excludes .git');

    ($exit, $out) = run_cmd($^X, script('Perl/repo_tools/todo_report.pl'), '--path', $dir, '--format', 'markdown');
    like($out, qr/\| File \| Line \| Marker \| Message \|/, 'emits markdown table');
};

subtest 'env_audit reports structure without leaking values' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $env = "$dir/.env";
    my $example = "$dir/.env.example";
    write_file($example, "APP_ENV=\nAPI_TOKEN=\nMODEL_NAME=llama3\nBAD-NAME=value\n");
    write_file($env, "APP_ENV=local\nAPP_ENV=duplicate\nEXTRA=yes\nEMPTY=\nAPI_TOKEN=supersecret\n");

    my ($exit, $out) = run_cmd($^X, script('Perl/config_tools/env_audit.pl'), '--env', $env, '--example', $example, '--json');
    my $data = decode_json($out);
    is($exit, 1, 'env audit exits non-zero on issues');
    is_deeply($data->{missing_keys}, ['MODEL_NAME'], 'reports missing keys');
    is_deeply($data->{extra_keys}, ['EMPTY', 'EXTRA'], 'reports extra keys');
    is(scalar @{ $data->{duplicate_keys} }, 1, 'reports duplicate keys');
    is(scalar @{ $data->{invalid_keys} }, 1, 'reports invalid example key');
    unlike($out, qr/supersecret/, 'does not leak secret values');
};

subtest 'replace_in_files previews, writes backups, and filters by extension' => sub {
    my $dir = tempdir(CLEANUP => 1);
    write_file("$dir/a.txt", "hello alpha\nalpha again\n");
    write_file("$dir/b.md", "alpha docs\n");

    my ($exit, $out) = run_cmd($^X, script('Perl/text_tools/replace_in_files.pl'), '--path', $dir, '--find', 'alpha', '--replace', 'beta', '--include', 'txt');
    is($exit, 0, 'dry-run exits zero');
    like($out, qr/Would change/, 'previews changes');
    like(read_file("$dir/a.txt"), qr/alpha/, 'dry-run does not write');

    ($exit, $out) = run_cmd($^X, script('Perl/text_tools/replace_in_files.pl'), '--path', $dir, '--find', 'alpha', '--replace', 'beta', '--include', 'txt', '--write', '--backup');
    is($exit, 0, 'write exits zero');
    like(read_file("$dir/a.txt"), qr/beta/, 'writes replacement');
    ok(-f "$dir/a.txt.bak", 'creates backup');
    like(read_file("$dir/b.md"), qr/alpha/, 'respects include filter');
};

subtest 'log_summary counts severities and repeated messages' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $log = "$dir/app.log";
    write_file(
        $log,
        "2026-06-19 10:00:00 INFO started\n" .
        "2026-06-19 10:00:01 ERROR failed connect\n" .
        "2026-06-19 10:00:02 ERROR failed connect\n" .
        "2026-06-19 10:00:03 WARN slow request\n",
    );

    my ($exit, $out) = run_cmd($^X, script('Perl/log_tools/log_summary.pl'), '--file', $log, '--top', '2', '--json');
    my $data = decode_json($out);
    is($exit, 0, 'log summary exits zero');
    is($data->{severity}{ERROR}, 2, 'counts errors');
    is($data->{severity}{WARN}, 1, 'counts warnings');
    is($data->{top_messages}[0]{message}, 'failed connect', 'normalizes repeated messages');
};

subtest 'repo_lint detects issues and clean fixtures' => sub {
    my $bad = tempdir(CLEANUP => 1);
    write_file("$bad/bad.md", "ok\nbad trailing   \n" . ('x' x 20) . "\n\tbad tab\n");
    write_file("$bad/large.txt", 'z' x 2048);

    my ($exit, $out) = run_cmd($^X, script('Perl/repo_tools/repo_lint.pl'), '--path', $bad, '--max-line', '10', '--max-size-kb', '1', '--json');
    my $data = decode_json($out);
    is($exit, 1, 'repo lint exits non-zero on issues');
    my %types = map { $_->{type} => 1 } @{ $data->{issues} };
    ok($types{trailing_whitespace}, 'detects trailing whitespace');
    ok($types{long_line}, 'detects long lines');
    ok($types{large_file}, 'detects large files');
    ok($types{tab_in_markdown}, 'detects markdown tabs');

    my $clean = tempdir(CLEANUP => 1);
    write_file("$clean/good.txt", "short line\n");
    ($exit, $out) = run_cmd($^X, script('Perl/repo_tools/repo_lint.pl'), '--path', $clean, '--max-line', '120');
    is($exit, 0, 'clean repo fixture exits zero');
    like($out, qr/No issues found/, 'reports clean fixture');
};

done_testing();
