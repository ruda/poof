poof:
	./poof.py

poof.pdf: poof.ps
	pstopdf poof.ps -o poof.pdf

poof.ps: poof.1
	groff -man poof.1 > poof.ps

clean:
	rm -f *~ *.ps *.pdf *.pyc
