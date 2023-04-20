.. _sphx_glr_ex_01-valve.py:


Valve expansion
===============


This examples shows how to use the embedding feature of PyMechanical.


Setting up model
----------------

Embed Mechanical and set global variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import os

    import ansys.mechanical.core as mech
    from ansys.mechanical.core.examples import download_file, delete_downloads

    app = mech.App(version=232)
    globals().update(mech.global_variables(app))
    print(app)

.. rst-class:: sphx-glr-script-out

 .. code-block:: none

    Ansys Mechanical [Ansys Mechanical Enterprise]
    Product Version:232

Download example file and add structural static analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")
    analysis = Model.AddStaticStructuralAnalysis()

Configure graphics for image export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    ExtAPI.Graphics.Camera.SetSpecificViewOrientation(
        Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso
    )
    ExtAPI.Graphics.Camera.SetFit()
    image_export_format = Ansys.Mechanical.DataModel.Enums.GraphicsImageExportFormat.PNG
    settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
    settings_720p.Resolution = (
        Ansys.Mechanical.DataModel.Enums.GraphicsResolutionType.EnhancedResolution
    )
    settings_720p.Background = Ansys.Mechanical.DataModel.Enums.GraphicsBackgroundType.White
    settings_720p.Width = 1280
    settings_720p.Capture = Ansys.Mechanical.DataModel.Enums.GraphicsCaptureType.ImageOnly
    settings_720p.Height = 720
    settings_720p.CurrentGraphicsDisplay = False

Import geometry
~~~~~~~~~~~~~~~

.. code-block:: python

    geometry_file = geometry_path
    geometry_import = Model.GeometryImportGroup.AddGeometryImport()
    geometry_import_format = (
        Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
    )
    geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
    geometry_import_preferences.ProcessNamedSelections = True
    geometry_import.Import(
        geometry_file, geometry_import_format, geometry_import_preferences
    )

    ExtAPI.Graphics.ExportImage(
        os.path.join(os.getcwd(), "geometry.png"), image_export_format, settings_720p
    )

.. image-sg:: /basic_examples/basic/images/sphx_glr_embedding_basic_01_geometry.png
   :alt: 21 valve geometry
   :srcset: /basic_examples/basic/images/sphx_glr_embedding_basic_01_geometry.png
   :class: sphx-glr-single-img


Assign materials
~~~~~~~~~~~~~~~~

.. code-block:: python

    material_assignment = Model.Materials.AddMaterialAssignment()
    material_assignment.Material = "Structural Steel"
    sel = ExtAPI.SelectionManager.CreateSelectionInfo(
        Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities
    )
    sel.Ids = [
        body.GetGeoBody().Id
        for body in Model.Geometry.GetChildren(
            Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Body, True
        )
    ]
    material_assignment.Location = sel

Define mesh settings,  generate mesh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    mesh = Model.Mesh
    mesh.ElementSize = Quantity(25, "mm")
    mesh.GenerateMesh()
    Tree.Activate([mesh])
    ExtAPI.Graphics.ExportImage(
        os.path.join(os.getcwd(), "mesh.png"), image_export_format, settings_720p
    )

Define boundary conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    fixed_support = analysis.AddFixedSupport()
    fixed_support.Location = ExtAPI.DataModel.GetObjectsByName("NSFixedSupportFaces")[0]

    frictionless_support = analysis.AddFrictionlessSupport()
    frictionless_support.Location = ExtAPI.DataModel.GetObjectsByName(
        "NSFrictionlessSupportFaces"
    )[0]

    pressure = analysis.AddPressure()
    pressure.Location = ExtAPI.DataModel.GetObjectsByName("NSInsideFaces")[0]

    pressure.Magnitude.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]")]
    pressure.Magnitude.Output.DiscreteValues = [Quantity("0 [Pa]"), Quantity("15 [MPa]")]

Run solution
------------

Solve model
~~~~~~~~~~~

.. note::
   The following code only changes the solver settings so that they run on the CI/CD of the GitHub infrastructure.

.. code-block:: python

    config = ExtAPI.Application.SolveConfigurations["My Computer"]
    config.SolveProcessSettings.MaxNumberOfCores = 1
    config.SolveProcessSettings.DistributeSolution = False
    Model.Solve()

Postprocessing
--------------

Evaluate results, export screenshots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    solution = analysis.Solution
    deformation = solution.AddTotalDeformation()
    stress = solution.AddEquivalentStress()
    solution.EvaluateAllResults()

    Tree.Activate([deformation])
    ExtAPI.Graphics.ExportImage(
        os.path.join(os.getcwd(), "deformation.png"), image_export_format, settings_720p
    )
    Tree.Activate([stress])
    ExtAPI.Graphics.ExportImage(
        os.path.join(os.getcwd(), "stress.png"), image_export_format, settings_720p
    )

.. image-sg:: /basic_examples/basic/images/sphx_glr_embedding_basic_01_deformation.png
   :alt: 21 valve deformation
   :srcset: /basic_examples/basic/images/sphx_glr_embedding_basic_01_deformation.png
   :class: sphx-glr-single-img

.. image-sg:: /basic_examples/basic/images/sphx_glr_embedding_basic_01_stress.png
   :alt: 21 valve stress
   :srcset: /basic_examples/basic/images/sphx_glr_embedding_basic_01_stress.png
   :class: sphx-glr-single-img

Export stress animation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    animation_export_format = (
        Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.MP4
    )
    settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
    settings_720p.Width = 1280
    settings_720p.Height = 720
    stress.ExportAnimation(
        os.path.join(os.getcwd(), "Valve.mp4"), animation_export_format, settings_720p
    )

Cleanup
-------

Save project
~~~~~~~~~~~~

.. code-block:: python

    app.save(os.path.join(os.getcwd(), "Valve.mechdat"))
    app.new()

Delete example file
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    delete_downloads()
