use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);
use JSON::PP qw(decode_json);

my $repo = $ENV{REPO_ROOT} || '.';

sub script { "$repo/Perl/data_tools/jsonl_validate.pl" }
sub sq { my ($v) = @_; $v =~ s/'/'"'"'/g; return "'$v'" }
sub run_cmd { my @parts = @_; my $out = qx(@{[join ' ', map { sq($_) } @parts]} 2>&1); return ($? >> 8, $out) }
sub write_file { my ($path, $content) = @_; open my $fh, '>:encoding(UTF-8)', $path or die $!; print {$fh} $content }

my $dir = tempdir(CLEANUP => 1);
my $file = "$dir/prompts.jsonl";
write_file($file, "{\"messages\":[]}\nnot-json\n{\"prompt\":\"hello\"}\n");

my ($exit, $out) = run_cmd($^X, script(), '--file', $file, '--require', 'messages', '--max-errors', '1', '--json');
my $data = decode_json($out);
is($exit, 1, 'invalid JSONL exits non-zero');
is($data->{total_lines}, 3, 'counts total lines');
is($data->{invalid_lines}, 1, 'counts invalid JSON');
is($data->{missing_lines}, 1, 'counts missing keys');
is(scalar @{ $data->{errors} }, 1, 'honors max error limit');

write_file($file, "{\"messages\":[]}\n");
($exit, $out) = run_cmd($^X, script(), '--file', $file, '--require', 'messages');
is($exit, 0, 'valid file exits zero');
like($out, qr/Valid lines: 1/, 'prints text summary');

write_file($file, "");
($exit, $out) = run_cmd($^X, script(), '--file', $file, '--json');
$data = decode_json($out);
is($exit, 0, 'empty file without requirements exits zero');
is($data->{total_lines}, 0, 'counts empty file');

done_testing();
