use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);

my $repo = $ENV{REPO_ROOT} || '.';

sub script { "$repo/Perl/text_tools/replace_in_files.pl" }
sub sq { my ($v) = @_; $v =~ s/'/'"'"'/g; return "'$v'" }
sub run_cmd { my @parts = @_; my $out = qx(@{[join ' ', map { sq($_) } @parts]} 2>&1); return ($? >> 8, $out) }
sub write_file { my ($path, $content) = @_; open my $fh, '>:encoding(UTF-8)', $path or die $!; print {$fh} $content }
sub read_file { my ($path) = @_; open my $fh, '<:encoding(UTF-8)', $path or die $!; local $/; return <$fh> }

my $dir = tempdir(CLEANUP => 1);
write_file("$dir/a.txt", "hello alpha\nalpha again\n");
write_file("$dir/b.md", "alpha docs\n");

my ($exit, $out) = run_cmd($^X, script(), '--path', $dir, '--find', 'alpha', '--replace', 'beta', '--include', 'txt');
is($exit, 0, 'dry-run exits zero');
like($out, qr/Would change/, 'previews changes');
like(read_file("$dir/a.txt"), qr/alpha/, 'dry-run does not write');

($exit, $out) = run_cmd($^X, script(), '--path', $dir, '--find', 'alpha', '--replace', 'beta', '--include', 'txt', '--write', '--backup');
is($exit, 0, 'write exits zero');
like(read_file("$dir/a.txt"), qr/beta/, 'writes replacement');
ok(-f "$dir/a.txt.bak", 'creates backup');
like(read_file("$dir/b.md"), qr/alpha/, 'respects include filter');

($exit, $out) = run_cmd($^X, script(), '--path', $dir, '--find', 'missing', '--replace', 'x', '--json');
like($out, qr/"changes":\[\]/, 'reports no JSON changes');

done_testing();
