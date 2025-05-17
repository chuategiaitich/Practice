#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
private slots:
    bool isSolved(int arr[][9]);
    bool isPossible(int arr[][9], int k,int x,int y);
    bool isInputValid(int arr[][9], int k,int x,int y);
    void on_reset_clicked();
    void on_solve_clicked();
};
#endif // MAINWINDOW_H
