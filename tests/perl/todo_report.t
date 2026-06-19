use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);
use File::Path qw(make_path);
use JSON::PP qw(decode_json);

my $repo = $ENV{REPO_ROOT} || '.';

sub script { "$repo/Perl/repo_tools/todo_report.pl" }
sub sq { my ($v) = @_; $v =~ s/'/'"'"'/g; return "'$v'" }
sub run_cmd { my @parts = @_; my $out = qx(@{[join ' ', map { sq($_) } @parts]} 2>&1); return ($? >> 8, $out) }
sub write_file { my ($path, $content) = @_; open my $fh, '>:encoding(UTF-8)', $path or die $!; print {$fh} $content }

my $dir = tempdir(CLEANUP => 1);
make_path("$dir/src", "$dir/.git", "$dir/vendor");
write_file("$dir/src/app.txt", "TODO: ship this\nplain\nFIXME handle edge\n");
write_file("$dir/.git/ignored.txt", "TODO: ignore this\n");
write_file("$dir/vendor/ignored.txt", "TODO: vendor ignore\n");

my ($exit, $out) = run_cmd($^X, script(), '--path', $dir, '--format', 'json', '--exclude', 'vendor');
my $data = decode_json($out);
is($exit, 0, 'todo report exits zero');
is($data->{count}, 2, 'finds markers outside excluded dirs');
unlike($out, qr/vendor ignore/, 'respects custom excludes');

($exit, $out) = run_cmd($^X, script(), '--path', $dir, '--format', 'markdown');
like($out, qr/\| File \| Line \| Marker \| Message \|/, 'prints markdown table');

($exit, $out) = run_cmd($^X, script(), '--path', $dir, '--format', 'bad');
is($exit, 255, 'invalid format fails');
like($out, qr/Invalid format/, 'reports invalid format');

done_testing();
