#!/usr/bin/env perl
use strict;
use warnings;
use File::Copy qw(copy);
use File::Find qw(find);
use Getopt::Long qw(GetOptions);
use JSON::PP qw(encode_json);

sub usage {
    return <<"USAGE";
Usage: $0 --path PATH --find REGEX --replace TEXT [--include EXT[,EXT...]] [--dry-run] [--write] [--backup] [--json]

Preview regex replacements by default. Use --write to modify files.
USAGE
}

sub split_csv {
    my ($value) = @_;
    return () unless defined $value && length $value;
    return grep { length $_ } map { s/^\s+|\s+$//gr } split /,/, $value;
}

sub extension_allowed {
    my ($path, $include) = @_;
    return 1 unless keys %$include;
    return $path =~ /\.([^.\/]+)\z/ && $include->{lc $1};
}

sub replace_in_files {
    my (%args) = @_;
    my $root    = $args{path};
    my $pattern = qr/$args{find}/;
    my $replace = $args{replace};
    my $write   = $args{write};
    my $backup  = $args{backup};
    my %include = map { lc($_) =~ s/^\.//r => 1 } @{ $args{include} || [] };
    my @changes;

    find(
        {
            wanted => sub {
                my $path = $File::Find::name;
                return unless -f $path;
                return unless extension_allowed($path, \%include);

                open my $fh, '<:encoding(UTF-8)', $path or return;
                local $/;
                my $original = <$fh>;
                close $fh;

                my $count = () = $original =~ /$pattern/g;
                return unless $count;

                my $updated = $original;
                $updated =~ s/$pattern/$replace/g;
                push @changes, { file => $path, matches => $count, changed => $write ? JSON::PP::true : JSON::PP::false };

                if ($write) {
                    copy($path, "$path.bak") or die "Could not create backup for '$path': $!\n" if $backup;
                    open my $out, '>:encoding(UTF-8)', $path or die "Could not write '$path': $!\n";
                    print {$out} $updated;
                }
            },
            no_chdir => 1,
        },
        $root
    );

    return \@changes;
}

sub print_text {
    my ($changes, $write) = @_;
    if (!@$changes) {
        print "No matches found.\n";
        return;
    }
    for my $change (@$changes) {
        my $action = $write ? 'Changed' : 'Would change';
        print "$action: $change->{file} ($change->{matches} match";
        print "es" if $change->{matches} != 1;
        print ")\n";
    }
}

sub main {
    my %opts = (dry_run => 1);
    GetOptions(
        'path=s'    => \$opts{path},
        'find=s'    => \$opts{find},
        'replace=s' => \$opts{replace},
        'include=s' => \$opts{include},
        'dry-run'   => sub { $opts{dry_run} = 1; $opts{write} = 0 },
        'write'     => sub { $opts{write} = 1; $opts{dry_run} = 0 },
        'backup'    => \$opts{backup},
        'json'      => \$opts{json},
        'help'      => \$opts{help},
    ) or die usage();

    if ($opts{help}) {
        print usage();
        return 0;
    }
    die usage() unless defined $opts{path} && defined $opts{find} && defined $opts{replace};

    my @include = split_csv($opts{include});
    my $changes = replace_in_files(
        path    => $opts{path},
        find    => $opts{find},
        replace => $opts{replace},
        include => \@include,
        write   => $opts{write},
        backup  => $opts{backup},
    );

    if ($opts{json}) {
        print encode_json({ dry_run => $opts{write} ? JSON::PP::false : JSON::PP::true, changes => $changes }) . "\n";
    } else {
        print_text($changes, $opts{write});
    }
    return 0;
}

exit main() unless caller;
