use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);
use File::Path qw(make_path);
use JSON::PP qw(decode_json);

my $repo = $ENV{REPO_ROOT} || '.';

sub script { "$repo/Perl/repo_tools/repo_lint.pl" }
sub sq { my ($v) = @_; $v =~ s/'/'"'"'/g; return "'$v'" }
sub run_cmd { my @parts = @_; my $out = qx(@{[join ' ', map { sq($_) } @parts]} 2>&1); return ($? >> 8, $out) }
sub write_file { my ($path, $content) = @_; open my $fh, '>:encoding(UTF-8)', $path or die $!; print {$fh} $content }

my $bad = tempdir(CLEANUP => 1);
write_file("$bad/bad.md", "ok\nbad trailing   \n" . ('x' x 20) . "\n\tbad tab\n");
write_file("$bad/large.txt", 'z' x 2048);

my ($exit, $out) = run_cmd($^X, script(), '--path', $bad, '--max-line', '10', '--max-size-kb', '1', '--json');
my $data = decode_json($out);
is($exit, 1, 'repo lint exits non-zero on issues');
my %types = map { $_->{type} => 1 } @{ $data->{issues} };
ok($types{trailing_whitespace}, 'detects trailing whitespace');
ok($types{long_line}, 'detects long lines');
ok($types{large_file}, 'detects large files');
ok($types{tab_in_markdown}, 'detects markdown tabs');

my $clean = tempdir(CLEANUP => 1);
make_path("$clean/.git");
write_file("$clean/good.txt", "short line\n");
write_file("$clean/.git/ignored.txt", ('x' x 200) . "\n");
($exit, $out) = run_cmd($^X, script(), '--path', $clean, '--max-line', '120');
is($exit, 0, 'clean repo fixture exits zero');
like($out, qr/No issues found/, 'reports clean fixture and skips excludes');

done_testing();
