package traceuse;
use strict;
use warnings;
use Devel::Symdump;

sub import {
  my $class = shift;
  my $module = shift;

  my $caller = caller();

  my $before = Devel::Symdump->new($caller);

  my $args = \@_;
  # more robust way of emulating use?
  eval "package $caller; require $module; $module\->import(\@\$args)";

  my $after = Devel::Symdump->new($caller);

  my @added;
  my @after_subs = $after->functions;
  my %before_subs = map { ($_,1) } $before->functions;
  for my $k (@after_subs) {
    push(@added, $k) unless $before_subs{$k};
  }

  if (@added) {
    warn "using module $module added: ".join(' ', @added)."\n";
  } else {
    warn "no new symbols from using module $module\n";
  }
}
1;
