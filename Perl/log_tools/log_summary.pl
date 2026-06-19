#!/usr/bin/env perl
use strict;
use warnings;
use Getopt::Long qw(GetOptions);
use JSON::PP qw(encode_json);

sub usage {
    return <<"USAGE";
Usage: $0 --file PATH [--top N] [--json]

Summarize generic application logs by severity and repeated message.
USAGE
}

sub clean_message {
    my ($line) = @_;
    chomp $line;
    $line =~ s/^\s*\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?\s*//;
    $line =~ s/^\[[^\]]+\]\s*//;
    $line =~ s/\b(?:ERROR|WARN|WARNING|INFO|DEBUG)\b[:\s-]*//i;
    $line =~ s/^\s+|\s+$//g;
    return $line || '(empty message)';
}

sub summarize_log {
    my (%args) = @_;
    my $file = $args{file};
    my $top  = $args{top} || 10;
    open my $fh, '<:encoding(UTF-8)', $file or die "Could not open '$file': $!\n";

    my %severity = map { $_ => 0 } qw(ERROR WARN INFO DEBUG OTHER);
    my %messages;
    my $total = 0;
    while (my $line = <$fh>) {
        $total++;
        my $level = 'OTHER';
        if ($line =~ /\b(ERROR|WARN|WARNING|INFO|DEBUG)\b/i) {
            $level = uc($1);
            $level = 'WARN' if $level eq 'WARNING';
        }
        $severity{$level}++;
        $messages{clean_message($line)}++;
    }

    my @top_messages = map {
        { message => $_, count => $messages{$_} }
    } (sort { $messages{$b} <=> $messages{$a} || $a cmp $b } keys %messages)[0 .. ($top - 1 < keys(%messages) - 1 ? $top - 1 : keys(%messages) - 1)];

    return { file => $file, total_lines => $total, severity => \%severity, top_messages => \@top_messages };
}

sub print_text {
    my ($report) = @_;
    print "File: $report->{file}\n";
    print "Total lines: $report->{total_lines}\n";
    print "Severity counts:\n";
    for my $level (qw(ERROR WARN INFO DEBUG OTHER)) {
        print "  $level: $report->{severity}{$level}\n";
    }
    print "Top messages:\n";
    for my $item (@{ $report->{top_messages} }) {
        print "  $item->{count}  $item->{message}\n";
    }
}

sub main {
    my %opts = (top => 10);
    GetOptions(
        'file=s' => \$opts{file},
        'top=i'  => \$opts{top},
        'json'   => \$opts{json},
        'help'   => \$opts{help},
    ) or die usage();

    if ($opts{help}) {
        print usage();
        return 0;
    }
    die usage() unless $opts{file};

    my $report = summarize_log(file => $opts{file}, top => $opts{top});
    if ($opts{json}) {
        print encode_json($report) . "\n";
    } else {
        print_text($report);
    }
    return 0;
}

exit main() unless caller;
