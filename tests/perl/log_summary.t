use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);
use JSON::PP qw(decode_json);

my $repo = $ENV{REPO_ROOT} || '.';

sub script { "$repo/Perl/log_tools/log_summary.pl" }
sub sq { my ($v) = @_; $v =~ s/'/'"'"'/g; return "'$v'" }
sub run_cmd { my @parts = @_; my $out = qx(@{[join ' ', map { sq($_) } @parts]} 2>&1); return ($? >> 8, $out) }
sub write_file { my ($path, $content) = @_; open my $fh, '>:encoding(UTF-8)', $path or die $!; print {$fh} $content }

my $dir = tempdir(CLEANUP => 1);
my $log = "$dir/app.log";
write_file($log, "2026-06-19 10:00:00 INFO started\n2026-06-19 10:00:01 ERROR failed connect\n2026-06-19 10:00:02 ERROR failed connect\n2026-06-19 10:00:03 WARN slow request\nplain line\n");

my ($exit, $out) = run_cmd($^X, script(), '--file', $log, '--top', '2', '--json');
my $data = decode_json($out);
is($exit, 0, 'log summary exits zero');
is($data->{severity}{ERROR}, 2, 'counts errors');
is($data->{severity}{WARN}, 1, 'counts warnings');
is($data->{severity}{OTHER}, 1, 'counts other lines');
is($data->{top_messages}[0]{message}, 'failed connect', 'normalizes repeated messages');

($exit, $out) = run_cmd($^X, script(), '--file', $log, '--top', '1');
like($out, qr/Severity counts:/, 'prints text output');

done_testing();
