#!/usr/bin/env perl
use strict;
use warnings;
use Getopt::Long qw(GetOptions);
use JSON::PP qw(decode_json encode_json);

sub usage {
    return <<"USAGE";
Usage: $0 --file PATH [--require key1,key2] [--max-errors N] [--json]

Validate a JSONL file and optionally require top-level keys.
USAGE
}

sub parse_required_keys {
    my ($value) = @_;
    return () unless defined $value && length $value;
    return grep { length $_ } map { s/^\s+|\s+$//gr } split /,/, $value;
}

sub validate_jsonl {
    my (%args) = @_;
    my $file       = $args{file};
    my @required   = @{ $args{required} || [] };
    my $max_errors = $args{max_errors} || 25;

    open my $fh, '<:encoding(UTF-8)', $file or die "Could not open '$file': $!\n";

    my %summary = (
        file           => $file,
        total_lines    => 0,
        valid_lines    => 0,
        invalid_lines  => 0,
        missing_lines  => 0,
        errors         => [],
    );

    while (my $line = <$fh>) {
        $summary{total_lines}++;
        chomp $line;
        my $line_no = $summary{total_lines};

        my $record;
        eval { $record = decode_json($line); 1 } or do {
            $summary{invalid_lines}++;
            push @{ $summary{errors} }, { line => $line_no, type => 'invalid_json', message => "$@" }
                if @{ $summary{errors} } < $max_errors;
            next;
        };

        my @missing = grep { !exists $record->{$_} } @required;
        if (@missing) {
            $summary{missing_lines}++;
            push @{ $summary{errors} }, { line => $line_no, type => 'missing_keys', keys => \@missing }
                if @{ $summary{errors} } < $max_errors;
            next;
        }

        $summary{valid_lines}++;
    }

    return \%summary;
}

sub print_text {
    my ($summary) = @_;
    print "File: $summary->{file}\n";
    print "Total lines: $summary->{total_lines}\n";
    print "Valid lines: $summary->{valid_lines}\n";
    print "Invalid JSON lines: $summary->{invalid_lines}\n";
    print "Missing-key lines: $summary->{missing_lines}\n";
    for my $error (@{ $summary->{errors} }) {
        if ($error->{type} eq 'missing_keys') {
            print "Line $error->{line}: missing keys: " . join(', ', @{ $error->{keys} }) . "\n";
        } else {
            my $message = $error->{message};
            $message =~ s/\s+$//;
            print "Line $error->{line}: invalid JSON: $message\n";
        }
    }
}

sub main {
    my %opts = (max_errors => 25);
    GetOptions(
        'file=s'       => \$opts{file},
        'require=s'    => \$opts{require},
        'max-errors=i' => \$opts{max_errors},
        'json'         => \$opts{json},
        'help'         => \$opts{help},
    ) or die usage();

    if ($opts{help}) {
        print usage();
        return 0;
    }
    die usage() unless $opts{file};

    my @required = parse_required_keys($opts{require});
    my $summary = validate_jsonl(
        file       => $opts{file},
        required   => \@required,
        max_errors => $opts{max_errors},
    );

    if ($opts{json}) {
        print encode_json($summary) . "\n";
    } else {
        print_text($summary);
    }

    return ($summary->{invalid_lines} || $summary->{missing_lines}) ? 1 : 0;
}

exit main() unless caller;
