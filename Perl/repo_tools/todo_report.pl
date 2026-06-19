#!/usr/bin/env perl
use strict;
use warnings;
use File::Find qw(find);
use File::Spec;
use Getopt::Long qw(GetOptions);
use JSON::PP qw(encode_json);

my @DEFAULT_EXCLUDES = qw(.git .venv __pycache__ .pytest_cache .ruff_cache node_modules);

sub usage {
    return <<"USAGE";
Usage: $0 [--path PATH] [--format text|markdown|json] [--exclude DIR[,DIR...]]

Scan files for TODO, FIXME, HACK, and NOTE markers.
USAGE
}

sub split_csv {
    my ($value) = @_;
    return () unless defined $value && length $value;
    return grep { length $_ } map { s/^\s+|\s+$//gr } split /,/, $value;
}

sub should_skip {
    my ($path, $exclude) = @_;
    my @parts = File::Spec->splitdir($path);
    for my $part (@parts) {
        return 1 if $exclude->{$part};
    }
    return 0;
}

sub scan_todos {
    my (%args) = @_;
    my $root = $args{path} || '.';
    my %exclude = map { $_ => 1 } @{ $args{exclude} || [] };
    my @items;

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

                open my $fh, '<:encoding(UTF-8)', $path or return;
                my $line_no = 0;
                while (my $line = <$fh>) {
                    $line_no++;
                    if ($line =~ /\b(TODO|FIXME|HACK|NOTE)\b[:\s-]*(.*)$/) {
                        my $message = $2;
                        $message =~ s/^\s+|\s+$//g;
                        push @items, {
                            file    => $path,
                            line    => $line_no,
                            marker  => $1,
                            message => $message,
                        };
                    }
                }
            },
            no_chdir => 1,
        },
        $root
    );

    return \@items;
}

sub print_report {
    my ($items, $format) = @_;
    if ($format eq 'json') {
        print encode_json({ count => scalar(@$items), items => $items }) . "\n";
        return;
    }
    if ($format eq 'markdown') {
        print "| File | Line | Marker | Message |\n";
        print "| --- | ---: | --- | --- |\n";
        for my $item (@$items) {
            print "| $item->{file} | $item->{line} | $item->{marker} | $item->{message} |\n";
        }
        return;
    }
    for my $item (@$items) {
        print "$item->{file}:$item->{line}: $item->{marker}: $item->{message}\n";
    }
}

sub main {
    my %opts = (path => '.', format => 'text');
    GetOptions(
        'path=s'    => \$opts{path},
        'format=s'  => \$opts{format},
        'exclude=s' => \$opts{exclude},
        'help'      => \$opts{help},
    ) or die usage();

    if ($opts{help}) {
        print usage();
        return 0;
    }
    die "Invalid format: $opts{format}\n" unless $opts{format} =~ /\A(?:text|markdown|json)\z/;

    my @exclude = (@DEFAULT_EXCLUDES, split_csv($opts{exclude}));
    my $items = scan_todos(path => $opts{path}, exclude => \@exclude);
    print_report($items, $opts{format});
    return 0;
}

exit main() unless caller;
