# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 17:06:18 2023

@author: pmaroneh
"""
import os

import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import download_file, delete_downloads

app = mech.App(version=232) # starts a non-graphical Mechanical session within the python.exe
globals().update(mech.global_variables(app)) # update global variables to get access to the same Model, DataModel, etc variables as in the Mechanical scripting console​
print(app)

geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")
analysis = Model.AddStaticStructuralAnalysis()

cwd = os.path.join(os.getcwd(), "out")

# Configure graphics for image export
ExtAPI.Graphics.Camera.SetSpecificViewOrientation(Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso)
ExtAPI.Graphics.Camera.SetFit()
image_export_format = Ansys.Mechanical.DataModel.Enums.GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = Ansys.Mechanical.DataModel.Enums.GraphicsResolutionType.EnhancedResolution
settings_720p.Background = Ansys.Mechanical.DataModel.Enums.GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Capture =  Ansys.Mechanical.DataModel.Enums.GraphicsCaptureType.ImageOnly
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# Import geometry
geometry_file = geometry_path
geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import.Import(geometry_file, geometry_import_format, geometry_import_preferences)

ExtAPI.Graphics.ExportImage(os.path.join(cwd, "geometry.png"), image_export_format, settings_720p)

# Assign materials
material_assignment = Model.Materials.AddMaterialAssignment()
material_assignment.Material = "Structural Steel"
sel = ExtAPI.SelectionManager.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
sel.Ids = [body.GetGeoBody().Id for body in Model.Geometry.GetChildren(Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Body, True)]
material_assignment.Location = sel

# Define mesh settings,  generate mesh
mesh = Model.Mesh
mesh.ElementSize = Quantity(25,  "mm")
mesh.GenerateMesh()
Tree.Activate([mesh])
ExtAPI.Graphics.ExportImage(os.path.join(cwd, "mesh.png"), image_export_format, settings_720p)

# Define boundary conditions

fixed_support = analysis.AddFixedSupport()
fixed_support.Location = ExtAPI.DataModel.GetObjectsByName("NSFixedSupportFaces")[0]

frictionless_support = analysis.AddFrictionlessSupport()
frictionless_support.Location = ExtAPI.DataModel.GetObjectsByName("NSFrictionlessSupportFaces")[0]

pressure = analysis.AddPressure()
pressure.Location = ExtAPI.DataModel.GetObjectsByName("NSInsideFaces")[0]

pressure.Magnitude.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]")]
pressure.Magnitude.Output.DiscreteValues = [Quantity("0 [Pa]"), Quantity("15 [MPa]")]

# Solve model
Model.Solve()

# Evaluate results, export screenshots
solution = analysis.Solution
deformation = solution.AddTotalDeformation()
stress = solution.AddEquivalentStress()
solution.EvaluateAllResults()

Tree.Activate([deformation])
ExtAPI.Graphics.ExportImage(os.path.join(cwd, "deformation.png"), image_export_format, settings_720p)
Tree.Activate([stress])
ExtAPI.Graphics.ExportImage(os.path.join(cwd, "stress.png"), image_export_format, settings_720p)

# Export stress animation
animation_export_format = Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.MP4
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

stress.ExportAnimation(os.path.join(cwd, "Valve.mp4"), animation_export_format, settings_720p)

# Save project
app.save(os.path.join(cwd, "Valve.mechdat"))
app.new()

# delete example file
delete_downloads()
