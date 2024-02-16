.PHONY: all build vim count clean

all: build count

build: 
	mkdir -p obj
	mkdir -p obj/src
	if [ -e obj/night-cones.aux ];\
	then\
		cp obj/night-cones.aux obj/night-cones_old.aux;\
	fi
	pdflatex -jobname night-cones -output-directory obj night-cones.tex
	cd obj && bibtex night-cones.aux
	latex_count=5 ; \
	while ! cmp -s obj/night-cones.aux obj/night-cones_old.aux && [ $$latex_count -gt 0 ] ;\
	do \
		echo "Rerunning latex....." ;\
		cp obj/night-cones.aux obj/night-cones_old.aux;\
		pdflatex -jobname night-cones -output-directory obj night-cones.tex ;\
		latex_count=`expr $$latex_count - 1` ;\
	done

vim: 
	mkdir -p obj
	mkdir -p obj/src
	if [ -e obj/night-cones.aux ];\
	then\
		cp obj/night-cones.aux obj/night-cones_old.aux;\
	fi
	pdflatex -jobname night-cones -output-directory obj -halt-on-error night-cones.tex
	cd obj && bibtex night-cones.aux
	latex_count=5 ; \
	while ! cmp -s obj/night-cones.aux obj/night-cones_old.aux && [ $$latex_count -gt 0 ] ;\
	do \
		echo "Rerunning latex....." ;\
		cp obj/night-cones.aux obj/night-cones_old.aux;\
		pdflatex -jobname night-cones -output-directory obj -halt-on-error night-cones.tex ;\
		latex_count=`expr $$latex_count - 1` ;\
	done

count:
	@echo
	@echo Counting words in abstract:
	@wc src/abstract_de.tex src/abstract_en.tex | grep abstract

clean:
	rm -f obj/*.aux
	rm -f obj/src/*.aux
	rm -f obj/*.bbl
	rm -f obj/*.blg
	rm -f obj/*.lof
	rm -f obj/*.log
	rm -f obj/*.lot
	rm -f obj/*.out
	rm -f obj/*.tdo
	rm -f obj/*.toc

cleanpdf:
	rm -f obj/*.aux
	rm -f obj/src/*.aux
	rm -f obj/*.bbl
	rm -f obj/*.blg
	rm -f obj/*.lof
	rm -f obj/*.log
	rm -f obj/*.lot
	rm -f obj/*.out
	rm -f obj/*.tdo
	rm -f obj/*.toc
	rm -f obj/*.pdf
