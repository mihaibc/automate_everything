#!/usr/bin/env perl
use strict;
use warnings;
use File::Find qw(find);
use File::Spec;
use Getopt::Long qw(GetOptions);
use JSON::PP qw(encode_json);

my @DEFAULT_EXCLUDES = qw(.git .venv __pycache__ .pytest_cache .ruff_cache node_modules automate_everything.egg-info);

sub usage {
    return <<"USAGE";
Usage: $0 [--path PATH] [--max-line N] [--max-size-kb N] [--json]

Run lightweight repository hygiene checks.
USAGE
}

sub should_skip {
    my ($path, $exclude) = @_;
    my @parts = File::Spec->splitdir($path);
    for my $part (@parts) {
        return 1 if $exclude->{$part};
    }
    return 0;
}

sub lint_repo {
    my (%args) = @_;
    my $root        = $args{path} || '.';
    my $max_line    = $args{max_line} || 120;
    my $max_size_kb = $args{max_size_kb} || 1024;
    my %exclude = map { $_ => 1 } @DEFAULT_EXCLUDES;
    my @issues;

    find(
        {
            wanted => sub {
                my $path = $File::Find::name;
                if (-d $path && should_skip($path, \%exclude)) {
                    $File::Find::prune = 1;
                    return;
                }
                return unless -f $path;
                return if should_skip($path, \%exclude);

                my $size_kb = (-s $path) / 1024;
                if ($size_kb > $max_size_kb) {
                    push @issues, { file => $path, type => 'large_file', size_kb => int($size_kb + 0.5) };
                }

                open my $fh, '<:encoding(UTF-8)', $path or do {
                    push @issues, { file => $path, type => 'read_error' };
                    return;
                };
                my $line_no = 0;
                while (my $line = <$fh>) {
                    $line_no++;
                    chomp $line;
                    push @issues, { file => $path, line => $line_no, type => 'trailing_whitespace' } if $line =~ /\s+\z/;
                    push @issues, { file => $path, line => $line_no, type => 'long_line', length => length($line) } if length($line) > $max_line;
                    push @issues, { file => $path, line => $line_no, type => 'tab_in_markdown' } if $path =~ /\.md\z/i && $line =~ /\t/;
                }
            },
            no_chdir => 1,
        },
        $root
    );

    return \@issues;
}

sub print_text {
    my ($issues) = @_;
    if (!@$issues) {
        print "No issues found.\n";
        return;
    }
    for my $issue (@$issues) {
        my $location = $issue->{file};
        $location .= ":$issue->{line}" if $issue->{line};
        print "$location: $issue->{type}\n";
    }
}

sub main {
    my %opts = (path => '.', max_line => 120, max_size_kb => 1024);
    GetOptions(
        'path=s'        => \$opts{path},
        'max-line=i'    => \$opts{max_line},
        'max-size-kb=i' => \$opts{max_size_kb},
        'json'          => \$opts{json},
        'help'          => \$opts{help},
    ) or die usage();

    if ($opts{help}) {
        print usage();
        return 0;
    }

    my $issues = lint_repo(path => $opts{path}, max_line => $opts{max_line}, max_size_kb => $opts{max_size_kb});
    if ($opts{json}) {
        print encode_json({ count => scalar(@$issues), issues => $issues }) . "\n";
    } else {
        print_text($issues);
    }
    return @$issues ? 1 : 0;
}

exit main() unless caller;
