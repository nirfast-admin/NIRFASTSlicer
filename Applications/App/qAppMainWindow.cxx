/*==============================================================================

  Copyright (c) Kitware, Inc.

  See http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Julien Finet, Kitware, Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// Qt includes
#include <QDebug>
#include <QTimer>

// Slicer includes
#include "qSlicerModuleSelectorToolBar.h"
#include "qSlicerModulesMenu.h"
#include "qSlicerModuleManager.h"
#include "qSlicerAbstractModule.h"

// SlicerApp includes
#include "qAppAboutDialog.h"
#include "qAppMainWindow_p.h"
#include "qSlicerApplication.h"

//-----------------------------------------------------------------------------
// qAppMainWindowPrivate methods

qAppMainWindowPrivate::qAppMainWindowPrivate(qAppMainWindow& object)
  : Superclass(object)
{
}

//-----------------------------------------------------------------------------
qAppMainWindowPrivate::~qAppMainWindowPrivate()
{
}

//-----------------------------------------------------------------------------
void qAppMainWindowPrivate::init()
{
  Q_Q(qAppMainWindow);
  this->Superclass::init();
}

//-----------------------------------------------------------------------------
void qAppMainWindowPrivate::setupUi(QMainWindow * mainWindow)
{
  this->Superclass::setupUi(mainWindow);

  qSlicerApplication * app = qSlicerApplication::application();

  mainWindow->setWindowTitle(app->applicationName());
  this->HelpAboutSlicerAppAction->setText("About " + app->applicationName());
  this->HelpAboutSlicerAppAction->setToolTip("");

  this->LogoLabel->setPixmap(QPixmap(":/LogoFull.png"));

  // Hide the toolbars
  this->MainToolBar->setVisible(false);
  //this->ModuleSelectorToolBar->setVisible(false);
  this->ModuleToolBar->setVisible(false);
  //this->ViewToolBar->setVisible(false);
  //this->MouseModeToolBar->setVisible(false);
  this->CaptureToolBar->setVisible(false);
  this->ViewersToolBar->setVisible(false);
  this->DialogToolBar->setVisible(false);

  // Hide the menus
  //this->menubar->setVisible(false);
  //this->FileMenu->setVisible(false);
  //this->EditMenu->setVisible(false);
  //this->ViewMenu->setVisible(false);
  //this->LayoutMenu->setVisible(false);
  //this->HelpMenu->setVisible(false);

  // Hide the modules panel
  //this->PanelDockWidget->setVisible(false);
  this->DataProbeCollapsibleWidget->setCollapsed(false);
  this->DataProbeCollapsibleWidget->setVisible(true);
  this->StatusBar->setVisible(true);
}

//-----------------------------------------------------------------------------
// qAppMainWindow methods

//-----------------------------------------------------------------------------
qAppMainWindow::qAppMainWindow(QWidget* windowParent)
  : Superclass(new qAppMainWindowPrivate(*this), windowParent)
{
  Q_D(qAppMainWindow);
  d->init();
}

//-----------------------------------------------------------------------------
qAppMainWindow::~qAppMainWindow()
{
}

//-----------------------------------------------------------------------------
void qAppMainWindow::on_HelpAboutSlicerAppAction_triggered()
{
  qAppAboutDialog about(this);
  about.exec();
}

//-----------------------------------------------------------------------------
void qAppMainWindow::show()
{
    Q_D(qAppMainWindow);

    qSlicerModulesMenu* qMenu = d->ModuleSelectorToolBar->modulesMenu();
    qSlicerModuleManager * moduleManager = qSlicerApplication::application()->moduleManager();

    // Modules to remove
    QStringList removeModuleNames = QStringList()
            << "Annotations"
            << "DICOM"
            << "Data"
            << "Editor"
            << "Markups"
            << "Models"
            << "SceneViews"
            << "SubjectHierarchy"
            << "Transforms"
            << "ViewControllers"
            << "VolumeRendering"
            << "Volumes"
            << "Segmentations";
    foreach(const QString& moduleName, removeModuleNames)
    {
        //qDebug()<<"Removing Module "<<moduleName;
        qSlicerAbstractCoreModule * coreModule = moduleManager->module(moduleName);
        qSlicerAbstractModule* module = qobject_cast<qSlicerAbstractModule*>(coreModule);
        qMenu->removeAction(module->action());
        // We removed the action but need to keep the connection for the
        // action in "All Modules", or if they are added back later on
        QObject::connect(module->action(), SIGNAL(triggered(bool)),
                         qMenu, SLOT(onActionTriggered()));
        //qDebug()<<"(-) Removed Module "<<module->name();
    }

    // Modules to add
    QStringList addModuleNames = QStringList()
            << "Home"
            << "DICOM"
            << "Data"
            << "ViewControllers"
            << "Volumes"
            << "VolumeRendering"
            << "CropVolume"
            << "SegmentEditor"
            << "Segmentations"
            << "Markups"
            << "Image2Mesh"
            << "Models";
    QAction * beforeAction = qMenu->actions().at(1); // to insert after the "All Modules" menu
    foreach(const QString& moduleName, addModuleNames)
    {
        //qDebug()<<"Adding Module "<<moduleName;
        qSlicerAbstractCoreModule * coreModule = moduleManager->module(moduleName);
        qSlicerAbstractModule* module = qobject_cast<qSlicerAbstractModule*>(coreModule);
        qMenu->insertAction(beforeAction, module->action());
        //qDebug()<<"(+) Added Module "<<module->name();
    }

    // Add missing separator (only if all modules removed from list)
    beforeAction = qMenu->actions().at(1);
    qMenu->insertSeparator(beforeAction);

    // Show
    this->Superclass::show();
}
