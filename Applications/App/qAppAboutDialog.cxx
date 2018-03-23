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

#include <QDebug>

// SlicerApp includes
#include "qAppAboutDialog.h"
#include "qSlicerApplication.h"
#include "ui_qAppAboutDialog.h"

//-----------------------------------------------------------------------------
class qAppAboutDialogPrivate: public Ui_qAppAboutDialog
{
public:
};

//-----------------------------------------------------------------------------
// qAppAboutDialogPrivate methods


//-----------------------------------------------------------------------------
// qAppAboutDialog methods
qAppAboutDialog::qAppAboutDialog(QWidget* parentWidget)
  : QDialog(parentWidget)
  , d_ptr(new qAppAboutDialogPrivate)
{
  Q_D(qAppAboutDialog);
  d->setupUi(this);
  qSlicerApplication* slicer = qSlicerApplication::application();
  d->CreditsTextBrowser->setFontPointSize(25);
  d->CreditsTextBrowser->append(slicer->applicationName());
  d->CreditsTextBrowser->setFontPointSize(11);
  d->CreditsTextBrowser->append("");
  d->CreditsTextBrowser->append(
    slicer->applicationVersion()+ " "
    + "r" + slicer->repositoryRevision());
  d->CreditsTextBrowser->append("");
  QString acknowledgmentText(
    "NIRFAST is NOT an FDA approved medical device.<br /><br />"
    "Supported by: NCI and the Slicer Community.<br /><br />"
    "This work is part of the National Cancer Center (NCI) grant titled <i>MRI"
    "Fluorescence Tomography for Quantifying Tumor Receptor Concentration in Vivo</i>."
    "NIRFAST is an open source software package for multi-modal optical imaging in "
    "living tissue. <br /><br />"
    "Originally developed at Dartmouth College in 2001, ongoing development, "
    "maintenance, distribution, and training is managed by Dartmouth College, University "
    "of Birmingham, and Kitware Inc. <br /><br />");
  d->CreditsTextBrowser->insertHtml(acknowledgmentText);
  d->CreditsTextBrowser->insertHtml(slicer->libraries());
    QString copyrightsText(
    "<table align=\"center\" border=\"0\" width=\"80%\"><tr>"
    "<td align=\"center\"><a href=\"https://github.com/nirfast-admin/NIRFASTSlicer/blob/master/License\">Licensing Information</a></td>"
    "<td align=\"center\"><a href=\"https://www.dartmouth.edu/~nir/nirfast/\">Website</a></td>"
    "</tr></table>");
  d->SlicerLinksTextBrowser->insertHtml(copyrightsText);
  d->CreditsTextBrowser->moveCursor(QTextCursor::Start, QTextCursor::MoveAnchor);
}

//-----------------------------------------------------------------------------
qAppAboutDialog::~qAppAboutDialog()
{
}
