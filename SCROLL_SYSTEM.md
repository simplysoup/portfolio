# V14 work rail

The work section uses a sticky viewport whose horizontal track follows native vertical scroll progress. On wide screens, each project card moves through the viewport as the page advances. There is no wheel capture, scroll locking, or scroll-jacking.

On small screens and when `prefers-reduced-motion: reduce` is active, the rail is disabled and all six projects appear in the regular vertical grid. The cards and their links remain ordinary, accessible content in either layout.
