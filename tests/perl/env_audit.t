use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);
use JSON::PP qw(decode_json);

my $repo = $ENV{REPO_ROOT} || '.';

sub script { "$repo/Perl/config_tools/env_audit.pl" }
sub sq { my ($v) = @_; $v =~ s/'/'"'"'/g; return "'$v'" }
sub run_cmd { my @parts = @_; my $out = qx(@{[join ' ', map { sq($_) } @parts]} 2>&1); return ($? >> 8, $out) }
sub write_file { my ($path, $content) = @_; open my $fh, '>:encoding(UTF-8)', $path or die $!; print {$fh} $content }

my $dir = tempdir(CLEANUP => 1);
my $env = "$dir/.env";
my $example = "$dir/.env.example";
write_file($example, "APP_ENV=\nAPI_TOKEN=\nMODEL_NAME=llama3\nBAD-NAME=value\n");
write_file($env, "APP_ENV=local\nAPP_ENV=duplicate\nEXTRA=yes\nEMPTY=\nAPI_TOKEN=supersecret\n");

my ($exit, $out) = run_cmd($^X, script(), '--env', $env, '--example', $example, '--json');
my $data = decode_json($out);
is($exit, 1, 'env audit exits non-zero on issues');
is_deeply($data->{missing_keys}, ['MODEL_NAME'], 'reports missing keys');
is_deeply($data->{extra_keys}, ['EMPTY', 'EXTRA'], 'reports extra keys');
is(scalar @{ $data->{duplicate_keys} }, 1, 'reports duplicate keys');
is(scalar @{ $data->{invalid_keys} }, 1, 'reports invalid keys');
unlike($out, qr/supersecret/, 'does not leak secret values');

write_file($env, "APP_ENV=local\nAPI_TOKEN=value\nMODEL_NAME=llama3\n");
write_file($example, "APP_ENV=\nAPI_TOKEN=\nMODEL_NAME=\n");
($exit, $out) = run_cmd($^X, script(), '--env', $env, '--example', $example);
is($exit, 0, 'clean env exits zero');
like($out, qr/Missing keys: none/, 'prints text output');

done_testing();
