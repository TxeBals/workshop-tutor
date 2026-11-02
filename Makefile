# Shortcuts for Linux/macOS. On Windows: python scripts/tasks.py <task>
.PHONY: setup test solutions catchup demo evals reset starters
setup:     ; python scripts/tasks.py setup
test:      ; python scripts/tasks.py test $(LAB)
lab%:      ; python scripts/tasks.py test $*
solutions: ; python scripts/tasks.py solutions
catchup:   ; python scripts/tasks.py catchup $(LAB)
demo:      ; python scripts/tasks.py demo
evals:     ; python scripts/tasks.py evals $(ARGS)
reset:     ; python scripts/tasks.py reset
starters:  ; python scripts/tasks.py starters
