#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QString>
#include <stdbool.h>
#include <QMessageBox>
#include <QRegularExpressionValidator>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    foreach(QLineEdit *le, findChildren<QLineEdit*>())
    {
        le->setValidator(new QRegularExpressionValidator(QRegularExpression("[1-9]\\d{0,0}"),this));

    }
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_solve_clicked()
{
    QString position[9][9];//gọi giá trị của ô từ string
    position[0][0]=ui->n0_0->text();position[0][1]=ui->n0_1->text();position[0][2]=ui->n0_2->text();position[0][3]=ui->n0_3->text();position[0][4]=ui->n0_4->text();position[0][5]=ui->n0_5->text();position[0][6]=ui->n0_6->text();position[0][7]=ui->n0_7->text();position[0][8]=ui->n0_8->text();
    position[1][0]=ui->n1_0->text();position[1][1]=ui->n1_1->text();position[1][2]=ui->n1_2->text();position[1][3]=ui->n1_3->text();position[1][4]=ui->n1_4->text();position[1][5]=ui->n1_5->text();position[1][6]=ui->n1_6->text();position[1][7]=ui->n1_7->text();position[1][8]=ui->n1_8->text();
    position[2][0]=ui->n2_0->text();position[2][1]=ui->n2_1->text();position[2][2]=ui->n2_2->text();position[2][3]=ui->n2_3->text();position[2][4]=ui->n2_4->text();position[2][5]=ui->n2_5->text();position[2][6]=ui->n2_6->text();position[2][7]=ui->n2_7->text();position[2][8]=ui->n2_8->text();
    position[3][0]=ui->n3_0->text();position[3][1]=ui->n3_1->text();position[3][2]=ui->n3_2->text();position[3][3]=ui->n3_3->text();position[3][4]=ui->n3_4->text();position[3][5]=ui->n3_5->text();position[3][6]=ui->n3_6->text();position[3][7]=ui->n3_7->text();position[3][8]=ui->n3_8->text();
    position[4][0]=ui->n4_0->text();position[4][1]=ui->n4_1->text();position[4][2]=ui->n4_2->text();position[4][3]=ui->n4_3->text();position[4][4]=ui->n4_4->text();position[4][5]=ui->n4_5->text();position[4][6]=ui->n4_6->text();position[4][7]=ui->n4_7->text();position[4][8]=ui->n4_8->text();
    position[5][0]=ui->n5_0->text();position[5][1]=ui->n5_1->text();position[5][2]=ui->n5_2->text();position[5][3]=ui->n5_3->text();position[5][4]=ui->n5_4->text();position[5][5]=ui->n5_5->text();position[5][6]=ui->n5_6->text();position[5][7]=ui->n5_7->text();position[5][8]=ui->n5_8->text();
    position[6][0]=ui->n6_0->text();position[6][1]=ui->n6_1->text();position[6][2]=ui->n6_2->text();position[6][3]=ui->n6_3->text();position[6][4]=ui->n6_4->text();position[6][5]=ui->n6_5->text();position[6][6]=ui->n6_6->text();position[6][7]=ui->n6_7->text();position[6][8]=ui->n6_8->text();
    position[7][0]=ui->n7_0->text();position[7][1]=ui->n7_1->text();position[7][2]=ui->n7_2->text();position[7][3]=ui->n7_3->text();position[7][4]=ui->n7_4->text();position[7][5]=ui->n7_5->text();position[7][6]=ui->n7_6->text();position[7][7]=ui->n7_7->text();position[7][8]=ui->n7_8->text();
    position[8][0]=ui->n8_0->text();position[8][1]=ui->n8_1->text();position[8][2]=ui->n8_2->text();position[8][3]=ui->n8_3->text();position[8][4]=ui->n8_4->text();position[8][5]=ui->n8_5->text();position[8][6]=ui->n8_6->text();position[8][7]=ui->n8_7->text();position[8][8]=ui->n8_8->text();

    int value[9][9] = {{0}};
    int k = 0, i = 0, j = 0;
    bool isValid = true;

    for(i=0;i<9;i++)//đổi từ Text sang Số
    {
        for(j=0;j<9;j++)
        {
            value[i][j]=position[i][j].toInt();
        }
    }

    for(i=0;i<9&&isValid;i++)//Kiểm tra trùng lặp
    {
        for(j=0;j<9&&isValid;j++)
        {
            k=value[i][j];
            if(k != 0 && !isInputValid(value, k, i, j))
            {
                QMessageBox::warning(this,"LỖI","Số đã bị trùng, vui lòng nhập lại");
                isValid = false;
            }
        }
    }

    if(isValid)//Ô trống chuyển sang màu xanh
    {
        if(value[0][0] == 0) ui->n0_0->setStyleSheet("background-color:lightgreen;");
        if(value[0][1] == 0) ui->n0_1->setStyleSheet("background-color:lightgreen;");
        if(value[0][2] == 0) ui->n0_2->setStyleSheet("background-color:lightgreen;");
        if(value[0][3] == 0) ui->n0_3->setStyleSheet("background-color:lightgreen;");
        if(value[0][4] == 0) ui->n0_4->setStyleSheet("background-color:lightgreen;");
        if(value[0][5] == 0) ui->n0_5->setStyleSheet("background-color:lightgreen;");
        if(value[0][6] == 0) ui->n0_6->setStyleSheet("background-color:lightgreen;");
        if(value[0][7] == 0) ui->n0_7->setStyleSheet("background-color:lightgreen;");
        if(value[0][8] == 0) ui->n0_8->setStyleSheet("background-color:lightgreen;");

        if(value[1][0] == 0) ui->n1_0->setStyleSheet("background-color:lightgreen;");
        if(value[1][1] == 0) ui->n1_1->setStyleSheet("background-color:lightgreen;");
        if(value[1][2] == 0) ui->n1_2->setStyleSheet("background-color:lightgreen;");
        if(value[1][3] == 0) ui->n1_3->setStyleSheet("background-color:lightgreen;");
        if(value[1][4] == 0) ui->n1_4->setStyleSheet("background-color:lightgreen;");
        if(value[1][5] == 0) ui->n1_5->setStyleSheet("background-color:lightgreen;");
        if(value[1][6] == 0) ui->n1_6->setStyleSheet("background-color:lightgreen;");
        if(value[1][7] == 0) ui->n1_7->setStyleSheet("background-color:lightgreen;");
        if(value[1][8] == 0) ui->n1_8->setStyleSheet("background-color:lightgreen;");

        if(value[2][0] == 0) ui->n2_0->setStyleSheet("background-color:lightgreen;");
        if(value[2][1] == 0) ui->n2_1->setStyleSheet("background-color:lightgreen;");
        if(value[2][2] == 0) ui->n2_2->setStyleSheet("background-color:lightgreen;");
        if(value[2][3] == 0) ui->n2_3->setStyleSheet("background-color:lightgreen;");
        if(value[2][4] == 0) ui->n2_4->setStyleSheet("background-color:lightgreen;");
        if(value[2][5] == 0) ui->n2_5->setStyleSheet("background-color:lightgreen;");
        if(value[2][6] == 0) ui->n2_6->setStyleSheet("background-color:lightgreen;");
        if(value[2][7] == 0) ui->n2_7->setStyleSheet("background-color:lightgreen;");
        if(value[2][8] == 0) ui->n2_8->setStyleSheet("background-color:lightgreen;");

        if(value[3][0] == 0) ui->n3_0->setStyleSheet("background-color:lightgreen;");
        if(value[3][1] == 0) ui->n3_1->setStyleSheet("background-color:lightgreen;");
        if(value[3][2] == 0) ui->n3_2->setStyleSheet("background-color:lightgreen;");
        if(value[3][3] == 0) ui->n3_3->setStyleSheet("background-color:lightgreen;");
        if(value[3][4] == 0) ui->n3_4->setStyleSheet("background-color:lightgreen;");
        if(value[3][5] == 0) ui->n3_5->setStyleSheet("background-color:lightgreen;");
        if(value[3][6] == 0) ui->n3_6->setStyleSheet("background-color:lightgreen;");
        if(value[3][7] == 0) ui->n3_7->setStyleSheet("background-color:lightgreen;");
        if(value[3][8] == 0) ui->n3_8->setStyleSheet("background-color:lightgreen;");

        if(value[4][0] == 0) ui->n4_0->setStyleSheet("background-color:lightgreen;");
        if(value[4][1] == 0) ui->n4_1->setStyleSheet("background-color:lightgreen;");
        if(value[4][2] == 0) ui->n4_2->setStyleSheet("background-color:lightgreen;");
        if(value[4][3] == 0) ui->n4_3->setStyleSheet("background-color:lightgreen;");
        if(value[4][4] == 0) ui->n4_4->setStyleSheet("background-color:lightgreen;");
        if(value[4][5] == 0) ui->n4_5->setStyleSheet("background-color:lightgreen;");
        if(value[4][6] == 0) ui->n4_6->setStyleSheet("background-color:lightgreen;");
        if(value[4][7] == 0) ui->n4_7->setStyleSheet("background-color:lightgreen;");
        if(value[4][8] == 0) ui->n4_8->setStyleSheet("background-color:lightgreen;");

        if(value[5][0] == 0) ui->n5_0->setStyleSheet("background-color:lightgreen;");
        if(value[5][1] == 0) ui->n5_1->setStyleSheet("background-color:lightgreen;");
        if(value[5][2] == 0) ui->n5_2->setStyleSheet("background-color:lightgreen;");
        if(value[5][3] == 0) ui->n5_3->setStyleSheet("background-color:lightgreen;");
        if(value[5][4] == 0) ui->n5_4->setStyleSheet("background-color:lightgreen;");
        if(value[5][5] == 0) ui->n5_5->setStyleSheet("background-color:lightgreen;");
        if(value[5][6] == 0) ui->n5_6->setStyleSheet("background-color:lightgreen;");
        if(value[5][7] == 0) ui->n5_7->setStyleSheet("background-color:lightgreen;");
        if(value[5][8] == 0) ui->n5_8->setStyleSheet("background-color:lightgreen;");

        if(value[6][0] == 0) ui->n6_0->setStyleSheet("background-color:lightgreen;");
        if(value[6][1] == 0) ui->n6_1->setStyleSheet("background-color:lightgreen;");
        if(value[6][2] == 0) ui->n6_2->setStyleSheet("background-color:lightgreen;");
        if(value[6][3] == 0) ui->n6_3->setStyleSheet("background-color:lightgreen;");
        if(value[6][4] == 0) ui->n6_4->setStyleSheet("background-color:lightgreen;");
        if(value[6][5] == 0) ui->n6_5->setStyleSheet("background-color:lightgreen;");
        if(value[6][6] == 0) ui->n6_6->setStyleSheet("background-color:lightgreen;");
        if(value[6][7] == 0) ui->n6_7->setStyleSheet("background-color:lightgreen;");
        if(value[6][8] == 0) ui->n6_8->setStyleSheet("background-color:lightgreen;");

        if(value[7][0] == 0) ui->n7_0->setStyleSheet("background-color:lightgreen;");
        if(value[7][1] == 0) ui->n7_1->setStyleSheet("background-color:lightgreen;");
        if(value[7][2] == 0) ui->n7_2->setStyleSheet("background-color:lightgreen;");
        if(value[7][3] == 0) ui->n7_3->setStyleSheet("background-color:lightgreen;");
        if(value[7][4] == 0) ui->n7_4->setStyleSheet("background-color:lightgreen;");
        if(value[7][5] == 0) ui->n7_5->setStyleSheet("background-color:lightgreen;");
        if(value[7][6] == 0) ui->n7_6->setStyleSheet("background-color:lightgreen;");
        if(value[7][7] == 0) ui->n7_7->setStyleSheet("background-color:lightgreen;");
        if(value[7][8] == 0) ui->n7_8->setStyleSheet("background-color:lightgreen;");

        if(value[8][0] == 0) ui->n8_0->setStyleSheet("background-color:lightgreen;");
        if(value[8][1] == 0) ui->n8_1->setStyleSheet("background-color:lightgreen;");
        if(value[8][2] == 0) ui->n8_2->setStyleSheet("background-color:lightgreen;");
        if(value[8][3] == 0) ui->n8_3->setStyleSheet("background-color:lightgreen;");
        if(value[8][4] == 0) ui->n8_4->setStyleSheet("background-color:lightgreen;");
        if(value[8][5] == 0) ui->n8_5->setStyleSheet("background-color:lightgreen;");
        if(value[8][6] == 0) ui->n8_6->setStyleSheet("background-color:lightgreen;");
        if(value[8][7] == 0) ui->n8_7->setStyleSheet("background-color:lightgreen;");
        if(value[8][8] == 0) ui->n8_8->setStyleSheet("background-color:lightgreen;");

        isSolved(value);

        for(int i = 0; i < 9; i++)
        {
            for(int j = 0; j < 9; j++)
            {
                position[i][j] = QString::number(value[i][j]);
            }
        }
        ui->n0_0->setText(position[0][0]);  ui->n1_0->setText(position[1][0]);  ui->n2_0->setText(position[2][0]);  ui->n3_0->setText(position[3][0]);  ui->n4_0->setText(position[4][0]);  ui->n5_0->setText(position[5][0]);  ui->n6_0->setText(position[6][0]);  ui->n7_0->setText(position[7][0]);  ui->n8_0->setText(position[8][0]);
        ui->n0_1->setText(position[0][1]);  ui->n1_1->setText(position[1][1]);  ui->n2_1->setText(position[2][1]);  ui->n3_1->setText(position[3][1]);  ui->n4_1->setText(position[4][1]);  ui->n5_1->setText(position[5][1]);  ui->n6_1->setText(position[6][1]);  ui->n7_1->setText(position[7][1]);  ui->n8_1->setText(position[8][1]);
        ui->n0_2->setText(position[0][2]);  ui->n1_2->setText(position[1][2]);  ui->n2_2->setText(position[2][2]);  ui->n3_2->setText(position[3][2]);  ui->n4_2->setText(position[4][2]);  ui->n5_2->setText(position[5][2]);  ui->n6_2->setText(position[6][2]);  ui->n7_2->setText(position[7][2]);  ui->n8_2->setText(position[8][2]);
        ui->n0_3->setText(position[0][3]);  ui->n1_3->setText(position[1][3]);  ui->n2_3->setText(position[2][3]);  ui->n3_3->setText(position[3][3]);  ui->n4_3->setText(position[4][3]);  ui->n5_3->setText(position[5][3]);  ui->n6_3->setText(position[6][3]);  ui->n7_3->setText(position[7][3]);  ui->n8_3->setText(position[8][3]);
        ui->n0_4->setText(position[0][4]);  ui->n1_4->setText(position[1][4]);  ui->n2_4->setText(position[2][4]);  ui->n3_4->setText(position[3][4]);  ui->n4_4->setText(position[4][4]);  ui->n5_4->setText(position[5][4]);  ui->n6_4->setText(position[6][4]);  ui->n7_4->setText(position[7][4]);  ui->n8_4->setText(position[8][4]);
        ui->n0_5->setText(position[0][5]);  ui->n1_5->setText(position[1][5]);  ui->n2_5->setText(position[2][5]);  ui->n3_5->setText(position[3][5]);  ui->n4_5->setText(position[4][5]);  ui->n5_5->setText(position[5][5]);  ui->n6_5->setText(position[6][5]);  ui->n7_5->setText(position[7][5]);  ui->n8_5->setText(position[8][5]);
        ui->n0_6->setText(position[0][6]);  ui->n1_6->setText(position[1][6]);  ui->n2_6->setText(position[2][6]);  ui->n3_6->setText(position[3][6]);  ui->n4_6->setText(position[4][6]);  ui->n5_6->setText(position[5][6]);  ui->n6_6->setText(position[6][6]);  ui->n7_6->setText(position[7][6]);  ui->n8_6->setText(position[8][6]);
        ui->n0_7->setText(position[0][7]);  ui->n1_7->setText(position[1][7]);  ui->n2_7->setText(position[2][7]);  ui->n3_7->setText(position[3][7]);  ui->n4_7->setText(position[4][7]);  ui->n5_7->setText(position[5][7]);  ui->n6_7->setText(position[6][7]);  ui->n7_7->setText(position[7][7]);  ui->n8_7->setText(position[8][7]);
        ui->n0_8->setText(position[0][8]);  ui->n1_8->setText(position[1][8]);  ui->n2_8->setText(position[2][8]);  ui->n3_8->setText(position[3][8]);  ui->n4_8->setText(position[4][8]);  ui->n5_8->setText(position[5][8]);  ui->n6_8->setText(position[6][8]);  ui->n7_8->setText(position[7][8]);  ui->n8_8->setText(position[8][8]);
    }
}

bool MainWindow::isInputValid(int value[][9],int k,int x,int y)
{
    int i = 0, j = 0;
    for(i = 0; i < 9; i++){
        if(i != x && value[i][y] == k){
            return false;
        }
    }

    for(j = 0; j < 9; j++){
        if(j != y && value[x][j] == k){
            if(x != i){
                return false;
            }
        }
    }

    for(i = 3 * (x / 3); i < 3 * (x / 3 + 1); i++){
        for(j = 3 * (y / 3); j < 3 * (y / 3 + 1); j++){
            if(value[i][j] == k){
                if(i != x || j != y){
                    return false;
                }
            }
        }
    }

    return true;
}

bool MainWindow::isSolved(int value[][9])
{
    int i, j, k;
    for(i = 0; i < 9; i++){
        for(j = 0; j < 9; j++){
            if(value[i][j] == 0){
                for(k = 1; k <= 9; k++){
                    if(isPossible(value, k, j, i)){
                        value[i][j] = k;
                        if(isSolved(value)){
                            return true;
                        }
                    }
                }
                value[i][j] = 0;
                return false;
            }
        }
    }
    return true;
}

bool MainWindow::isPossible(int value[][9],int k,int x,int y)
{
    int i = 0, j = 0;
    for(j = 0; j < 9; j++){
        if(value[y][j] == k){
            return false;
        }
    }

    for(i = 0; i < 9; i++){
        if(value[i][x] == k){
            return false;
        }
    }

    for(i = 3 * (y / 3); i < 3 * (y / 3 + 1); i++){
        for(j = 3 * (x / 3); j < 3 * (x / 3 + 1); j++){
            if(value[i][j] == k){
                return false;
            }
        }
    }
    return true;
}

void MainWindow::on_reset_clicked()
{
    foreach(QLineEdit* edit, findChildren<QLineEdit*>()) {
        edit->clear();
        edit->setStyleSheet("background-color:white;");
    }
}

