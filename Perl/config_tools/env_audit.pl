#!/usr/bin/env perl
use strict;
use warnings;
use Getopt::Long qw(GetOptions);
use JSON::PP qw(encode_json);

sub usage {
    return <<"USAGE";
Usage: $0 --env PATH --example PATH [--json]

Compare an .env file against an .env.example without printing secret values.
USAGE
}

sub parse_env_file {
    my ($path) = @_;
    open my $fh, '<:encoding(UTF-8)', $path or die "Could not open '$path': $!\n";

    my (%keys, %seen);
    my (@duplicates, @invalid, @empty);
    my $line_no = 0;
    while (my $line = <$fh>) {
        $line_no++;
        chomp $line;
        $line =~ s/^\s+|\s+$//g;
        next if $line eq '' || $line =~ /^#/;
        $line =~ s/^export\s+//;

        my ($key, $value) = split /=/, $line, 2;
        $key = '' unless defined $key;
        $value = '' unless defined $value;
        $key =~ s/^\s+|\s+$//g;

        my $is_valid = $key =~ /\A[A-Za-z_][A-Za-z0-9_]*\z/;
        push @invalid, { key => $key, line => $line_no } unless $is_valid;
        push @duplicates, { key => $key, line => $line_no } if $seen{$key}++;
        push @empty, { key => $key, line => $line_no } if $value eq '';
        $keys{$key} = 1 if length $key && $is_valid;
    }

    return {
        path       => $path,
        keys       => \%keys,
        duplicates => \@duplicates,
        invalid    => \@invalid,
        empty      => \@empty,
    };
}

sub audit_env {
    my (%args) = @_;
    my $env     = parse_env_file($args{env});
    my $example = parse_env_file($args{example});

    my @missing = sort grep { !$env->{keys}->{$_} } keys %{ $example->{keys} };
    my @extra   = sort grep { !$example->{keys}->{$_} } keys %{ $env->{keys} };

    return {
        env_file       => $args{env},
        example_file   => $args{example},
        missing_keys   => \@missing,
        extra_keys     => \@extra,
        duplicate_keys => $env->{duplicates},
        invalid_keys   => [ @{ $env->{invalid} }, @{ $example->{invalid} } ],
        empty_values   => $env->{empty},
    };
}

sub print_text {
    my ($report) = @_;
    print "Env file: $report->{env_file}\n";
    print "Example file: $report->{example_file}\n";
    print "Missing keys: " . (@{ $report->{missing_keys} } ? join(', ', @{ $report->{missing_keys} }) : 'none') . "\n";
    print "Extra keys: " . (@{ $report->{extra_keys} } ? join(', ', @{ $report->{extra_keys} }) : 'none') . "\n";
    print "Duplicate keys: " . (@{ $report->{duplicate_keys} } ? join(', ', map { $_->{key} } @{ $report->{duplicate_keys} }) : 'none') . "\n";
    print "Invalid keys: " . (@{ $report->{invalid_keys} } ? join(', ', map { $_->{key} } @{ $report->{invalid_keys} }) : 'none') . "\n";
    print "Empty values: " . (@{ $report->{empty_values} } ? join(', ', map { $_->{key} } @{ $report->{empty_values} }) : 'none') . "\n";
}

sub main {
    my %opts;
    GetOptions(
        'env=s'     => \$opts{env},
        'example=s' => \$opts{example},
        'json'      => \$opts{json},
        'help'      => \$opts{help},
    ) or die usage();

    if ($opts{help}) {
        print usage();
        return 0;
    }
    die usage() unless $opts{env} && $opts{example};

    my $report = audit_env(env => $opts{env}, example => $opts{example});
    if ($opts{json}) {
        print encode_json($report) . "\n";
    } else {
        print_text($report);
    }

    return (
        @{ $report->{missing_keys} }
            || @{ $report->{duplicate_keys} }
            || @{ $report->{invalid_keys} }
    ) ? 1 : 0;
}

exit main() unless caller;
