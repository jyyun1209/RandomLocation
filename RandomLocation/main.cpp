#include "MainWindow.h"
#include <QtWidgets/qapplication.h>

int main(int argc, char *argv[])
{
	QApplication app(argc, argv);
	MainWindow::instance().show();

	return app.exec();
}