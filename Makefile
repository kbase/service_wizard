SERVICE_CAPS = ServiceWizard
SPEC_FILE = ServiceWizard.spec
URL = https://kbase.us/services/service_wizard
DIR = $(shell pwd)
LIB_DIR = lib
SCRIPTS_DIR = scripts
TEST_DIR = test
TEST_SCRIPT_NAME = run_tests.sh


.PHONY: test

default: compile build-startup-script build-executable-script build-test-script

compile:
	kb-sdk compile $(SPEC_FILE) \
		--out $(LIB_DIR) \
		--pysrvname biokbase.$(SERVICE_CAPS).Server \
		--pyimplname biokbase.$(SERVICE_CAPS).Impl;
	touch $(LIB_DIR)/biokbase/__init__.py
	touch $(LIB_DIR)/biokbase/$(SERVICE_CAPS)/__init__.py

install-deps:
	bash deps/rancher-compose.sh

test:
	bash $(TEST_DIR)/$(TEST_SCRIPT_NAME)

clean:
	echo "No op"
	
