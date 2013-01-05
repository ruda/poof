PREFIX=/usr/local
BINDIR=$(PREFIX)/bin
MANDIR=$(PREFIX)/share/man

test:
	./poof.py

poof.ps: poof.1
	groff -man poof.1 > poof.ps

poof.pdf: poof.ps
	pstopdf poof.ps -o poof.pdf

install: poof.py poof.1
	if [ ! -d $(BINDIR) ] ; then \
		install -d $(BINDIR) ; fi
	install -m 755 poof.py $(BINDIR)/poof
	if [ ! -d $(MANDIR)/man1 ] ; then \
		install -d $(MANDIR)/man1 ; fi
	install -m 644 poof.1 $(MANDIR)/man1/poof.1

uninstall:
	rm -f $(BINDIR)/poof
	rm -f $(MANDIR)/man1/poof.1

clean:
	rm -f *~ *.ps *.pdf *.pyc
