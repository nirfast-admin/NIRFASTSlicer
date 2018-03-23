include(SlicerMacroBuildScriptedModule)

#-----------------------------------------------------------------------------
set(MODULE_NAME CreateMesh)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_RESOURCES
  )

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )
