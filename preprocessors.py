"""
Standard preprocessors for enabling syntax sugar in Nexsys2.
This module does not export anything useful, but does initialize
a `NexsysPreProcessorScheduler` on importing.

This file can (and is intented to) be extended following the format
used by the standard preprocessors.
"""
from engine.nexsys2lib import NexsysPreProcessorScheduler, PreProcOnce, PreProcUntilStable
import engine.nexsys2preproc as nexsys2preproc
########################### IMPORT PROCESSOR FN'S HERE ############################
########################### IMPORT PROCESSOR FN'S HERE ############################
scheduler = NexsysPreProcessorScheduler()
################################## PREPROCESSORS ##################################
scheduler.schedule(PreProcOnce,         nexsys2preproc.comments)        # Runs 1st
scheduler.schedule(PreProcOnce,         nexsys2preproc.const_values)
scheduler.schedule(PreProcOnce,         nexsys2preproc.domains)
scheduler.schedule(PreProcOnce,         nexsys2preproc.guess_values)
scheduler.schedule(PreProcUntilStable,  nexsys2preproc.conditionals)    # Runs last
################################## PREPROCESSORS ##################################
