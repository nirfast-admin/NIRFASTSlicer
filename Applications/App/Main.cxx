/*==============================================================================

  Copyright (c) Kitware, Inc.

  See http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware, Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// Slicer includes
#include "qSlicerApplication.h"
#include "qSlicerApplicationHelper.h"

// SlicerApp includes
#include "qAppMainWindow.h"
#include "Widgets/qAppStyle.h"

//
// NIRFASTSlicer includes
//

// MatlabModules includes
#include "NIRFASTSlicerMatlabModulesConfigure.h"

// Qt includes
#include <QDebug>
#include <QAction>
#include <QLabel>
#include <QLineEdit>
#include <QFormLayout>
#include <QCheckBox>

// Slicer includes
#include <qMRMLVolumePropertyNodeWidget.h>
#include <qSlicerModulePanel.h>
#include <qSlicerAbstractModuleRepresentation.h>
#include <qSlicerAbstractModuleWidget.h>

// CTK includes
#include <ctkCollapsibleButton.h>
#include <ctkVTKVolumePropertyWidget.h>


namespace
{

//-----------------------------------------------------------------------------
bool isPathWithinPathsList(const QString& dirPath, const QStringList& pathsList)
{
  QDir dirToCheck(dirPath);
  foreach(const QString& path, pathsList)
  {
    if (dirToCheck == QDir(path))
    {
      return true;
    }
  }
  return false;
}

//----------------------------------------------------------------------------
int SlicerAppMain(int argc, char* argv[])
{
  typedef qAppMainWindow SlicerMainWindowType;

  qSlicerApplicationHelper::preInitializeApplication(argv[0], new qAppStyle);

  qSlicerApplication app(argc, argv);
  if (app.returnCode() != -1)
    {
    return app.returnCode();
    }

  // Append Matlab module path to the additional paths
  QString matlabModulesPath = app.slicerHome() + "/" + MATLABMODULES_DIR;
  QStringList additionalPaths = app.revisionUserSettings()->value("Modules/AdditionalPaths").toStringList();
  if (!isPathWithinPathsList(matlabModulesPath, additionalPaths))
    {
    additionalPaths << matlabModulesPath;
    app.revisionUserSettings()->setValue("Modules/AdditionalPaths", additionalPaths);
    qDebug() << "Adding path to Modules/AdditionalPaths : " << matlabModulesPath.toLatin1();
    }

  QScopedPointer<SlicerMainWindowType> window;
  QScopedPointer<QSplashScreen> splashScreen;

  qSlicerApplicationHelper::postInitializeApplication<SlicerMainWindowType>(
        app, splashScreen, window);

  if (!window.isNull())
    {
    QString windowTitle = QString("%1 %2").arg(Slicer_MAIN_PROJECT_APPLICATION_NAME).arg(Slicer_VERSION);
    window->setWindowTitle(windowTitle);
    window->setHomeModuleCurrent();
    }

  qSlicerModuleManager * moduleManager = app.moduleManager();

  // Edit MatlabModuleGenerator widget
  qSlicerAbstractCoreModule * matlabModuleGenerator = moduleManager->module("MatlabModuleGenerator");
  qSlicerAbstractModuleWidget* matlabWidget = dynamic_cast<qSlicerAbstractModuleWidget*>(matlabModuleGenerator->widgetRepresentation());
  if(matlabWidget)
    {
    QLabel* matlabLabel = matlabWidget->findChild<QLabel*>("label_3");
    if(matlabLabel)
      {
      matlabLabel->hide();
      }
    QLineEdit* matlabLineEdit = matlabWidget->findChild<QLineEdit*>("lineEdit_MatlabScriptDirectory");
    if(matlabLineEdit)
      {
        matlabLineEdit->hide();
      }
    ctkCollapsibleButton* matlabCollapsibleButton = matlabWidget->findChild<ctkCollapsibleButton*>("CollapsibleButton");
    if(matlabCollapsibleButton)
      {
      matlabCollapsibleButton->hide();
      }
    }
  else
    {
    qWarning() << "Could not update UI for the module"<< matlabModuleGenerator->name();
    }

  // Edit volume rendering widget
  qSlicerAbstractCoreModule * volRenCoreModule = moduleManager->module("VolumeRendering");
  qSlicerAbstractModuleWidget* volRenModuleWidget = dynamic_cast<qSlicerAbstractModuleWidget*>(volRenCoreModule->widgetRepresentation());
  if(volRenModuleWidget)
    {
    qMRMLVolumePropertyNodeWidget* volPropNodeWidget = volRenModuleWidget->findChild<qMRMLVolumePropertyNodeWidget*>("VolumePropertyNodeWidget");
    QFormLayout* volRenDisplayLayout = volRenModuleWidget->findChild<QFormLayout*>("formLayout_11");
    if(volPropNodeWidget && volRenDisplayLayout)
      {
      ctkVTKVolumePropertyWidget* ctkVolPropWidget =
              volPropNodeWidget->findChild<ctkVTKVolumePropertyWidget*>("VolumeProperty");
      if(ctkVolPropWidget)
        {
        QCheckBox* shadeCheckBox = ctkVolPropWidget->findChild<QCheckBox*>("ShadeCheckBox");
        if(shadeCheckBox)
          {
          QCheckBox* newShadeCheckBox = new QCheckBox("", volRenModuleWidget);
          QObject::connect(newShadeCheckBox, SIGNAL(toggled(bool)), shadeCheckBox, SLOT(setChecked(bool)));
          QObject::connect(shadeCheckBox, SIGNAL(toggled(bool)), newShadeCheckBox, SLOT(setChecked(bool)));
          volRenDisplayLayout->addRow("Shade:", newShadeCheckBox );
          }
        }
      }
    }
  else
    {
    qWarning() << "Could not update UI for the module"<< volRenCoreModule->name();
    }

  // Update CreateMesh icon
  qSlicerAbstractCoreModule * meshCoreModule = moduleManager->module("CreateMesh");
  qSlicerAbstractModule* meshModule = qobject_cast<qSlicerAbstractModule*>(meshCoreModule);
  qSlicerAbstractCoreModule * modelsCoreModule = moduleManager->module("Colors");
  qSlicerAbstractModule* modelsModule = qobject_cast<qSlicerAbstractModule*>(modelsCoreModule);
  meshModule->action()->setIcon(modelsModule->action()->icon());

  // Open Help & acknowledgment
  qSlicerModulePanel* modulePanel = window->findChild<qSlicerModulePanel*>("ModulePanel");
  ctkCollapsibleButton* helpButton = modulePanel->findChild<ctkCollapsibleButton*>("HelpCollapsibleButton");
  helpButton->setCollapsed(false);

  return app.exec();
}

} // end of anonymous namespace

#include "qSlicerApplicationMainWrapper.cxx"
