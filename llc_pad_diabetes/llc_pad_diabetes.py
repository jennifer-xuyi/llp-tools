import sys
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFormLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QCheckBox, QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mticker
import numpy as np

class ToolWindow(QMainWindow):

    def __init__(self):
        super(ToolWindow, self).__init__()
        self.title = 'Classification LLC X PAD X Diabetes'
        self.width = 1300
        self.height = 950
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)
        self.setCentralWidget(ClassificationTool())
        self.setStyleSheet(
            '''
                QMainWindow {background-color: #fff}
                QGroupBox {font-weight: bold; font-size: 12pt; color: #333}
            '''
        )
        self.show()


class ClassificationTool(QWidget):

    def __init__(self):
        super(ClassificationTool, self).__init__()

        self.toolLayout = QGridLayout()
        self.setLayout(self.toolLayout)

        self.llc_options = {
            "1. Gangrene": [self.llc1Checked, 0],
            "2. Osteomyelitis, Foot": [self.llc2Checked, 0],
            "3. Skin Ulcer, Foot": [self.llc3Checked, 0],
            "4. Osteomyelitis, Lower Limb": [self.llc4Checked, 0],
            "5. Skin Ulcer, Lower Limb": [self.llc5Checked, 0],
            "6. Cellulitis, Lower Limb": [self.llc6Checked, 0],
            "7. Cellulitis, Toe": [self.llc7Checked, 0]
        }
        self.pad_options = {
            "PAD": [self.pad1Checked, 0], 
            "WO PAD": [self.pad2Checked, 0]
        }
        self.diabetes_options = {
            "Diabetes": [self.diabetes1Checked, 0],  
            "WO Diabetes": [self.diabetes2Checked, 0], 
            "WO Diabetes, Gangrene NEC": [self.diabetes3Checked, 0]
        }

        self.dataImport = self.getSourceData(path="llc_pad_diabetes_w_amps_10yrs.xlsx")

        self.resultsStats = {
            # IP & DS
            'discharges_and_ds': 0,	
            'alos': 0,
            'discharges_and_ds_per_pat': 0,
            'unique_patients_ip_ds': 0,
            'major_during': 0,	
            'minor_during':	0,
            'lpr_during': 0,	
            'major_1yr': 0,
            'minor_1yr': 0,
            'lpr_1yr': 0,
            'major_3yr': 0,	
            'minor_3yr': 0,
            'lpr_3yr': 0,	
            'major_5yr': 0,	
            'minor_5yr': 0,
            'lpr_5yr': 0,

            # ED
            'ed_v':	0,
            'unique_patients_ed': 0,
            'ed_visits_per_pat': 0,
            'major_amp_1yr': 0,
            'minor_amp_1yr': 0,
            'lower_pr_1yr': 0,
            'major_amp_3yr': 0,
            'minor_amp_3yr': 0,
            'lower_pr_3yr': 0,	
            'major_amp_5yr': 0,	
            'minor_amp_5yr': 0,
            'lower_pr_5yr': 0
        }

        self.toolLayout.addWidget(self.createOptions("LLC"), 0, 0)
        self.toolLayout.addWidget(self.createOptions("PAD"), 0, 1)
        self.toolLayout.addWidget(self.createOptions("Diabetes"), 0, 2)

        resultsBox = self.createOutputBox("Results")
        self.resultsLayout = QHBoxLayout()
        resultsBox.setLayout(self.resultsLayout)

        self.creatInfoCard()

        self.canvas = FigureCanvas(plt.Figure(figsize=(5, 7), dpi=200, tight_layout=True))
        self.resultsLayout.addWidget(self.canvas)
        self.insert_ax()

        self.toolLayout.addWidget(resultsBox, 1, 0, 2, 3)

    def getSourceData(self, path):
        df = pd.read_excel(path, sheet_name="srcdata")

        return df

    # creat form method

    def createOptions(self, opt_name):
        
        inputGroupBox = QGroupBox(opt_name)
        inputGroupBox.setFont(QFont('Open Sans', 10))
        inputLayout = QFormLayout()
        for opt in self.llc_options:
            b = QCheckBox(opt)
            b.setChecked(False)
            b.stateChanged.connect(self.llc_options[opt][0])
            b.stateChanged.connect(self.update_chart)
            inputLayout.addRow(b)

        inputGroupBox.setLayout(inputLayout)

        return inputGroupBox

    def createOutputBox(self, group_name):

        outputGroupBox = QGroupBox(group_name)
        outputGroupBox.setFont(QFont('Open Sans', 10))

        return outputGroupBox

    def infoText(self):
        return '''
                <span style=font-size:10pt> <em>Inpatient & Day Surgery</em> </span><br><br>
                Discherges & Day Surgeries: <span style=color:#b22222>{0[discharges_and_ds]:0.0f}</span> <br>
                ALOS: <span style=color:#b22222>{0[alos]:0.0f}</span> <br>
                Unique Patients: <span style=color:#b22222>{0[unique_patients_ip_ds]:0.0f}</span> <br>
                Discharges or Day Surgeries per Patient: <span style=color:#b22222>{0[discharges_and_ds_per_pat]:0.1f}</span> <br><br><br><br>

                <span style=font-size:10pt> <em>ED</em> </span><br><br>
                ED Visits: <span style=color:#b22222>{0[ed_v]:0.0f}</span> <br>
                Unique ED Patients: <span style=color:#b22222>{0[unique_patients_ed]:0.0f}</span> <br>
                ED Visits per Patient: <span style=color:#b22222>{0[ed_visits_per_pat]:0.1f}</span> <br><br>
            '''.format(self.resultsStats)

    def creatInfoCard(self):
        self.displayStats = QLabel()
        self.displayStats.setFont(QFont("Open Sans", 10))
        self.displayStats.setAlignment(Qt.AlignTop)	
        self.displayStats.setText(self.infoText())

        self.resultsLayout.addWidget(self.displayStats)

    def updateInfoCard(self):
        self.displayStats.setText(self.infoText())

    def diabetes1Checked(self, checked):

        if checked:
            self.diabetes_options["Diabetes"][1] = 1
        else:
            self.diabetes_options["Diabetes"][1] = 0

        self.dfFilterAndAgg()

    def diabetes2Checked(self, checked):

        if checked:
            self.diabetes_options["WO Diabetes"][1] = 1
        else:
            self.diabetes_options["WO Diabetes"][1] = 0

        self.dfFilterAndAgg()

    def diabetes3Checked(self, checked):

        if checked:
            self.diabetes_options["WO Diabetes, Gangrene NEC"][1] = 1
        else:
            self.diabetes_options["WO Diabetes, Gangrene NEC"][1] = 0

        self.dfFilterAndAgg()

    def pad1Checked(self, checked):

        if checked:
            self.pad_options["PAD"][1] = 1
        else:
            self.pad_options["PAD"][1] = 0

        self.dfFilterAndAgg()

    def pad2Checked(self, checked):

        if checked:
            self.pad_options["WO PAD"][1] = 1
        else:
            self.pad_options["WO PAD"][1] = 0

        self.dfFilterAndAgg()

    def llc1Checked(self, checked):

        if checked:
            self.llc_options["1. Gangrene"][1] = 1
        else:
            self.llc_options["1. Gangrene"][1] = 0

        self.dfFilterAndAgg()

    def llc2Checked(self, checked):

        if checked:
            self.llc_options["2. Osteomyelitis, Foot"][1] = 1
        else:
            self.llc_options["2. Osteomyelitis, Foot"][1] = 0
        
        self.dfFilterAndAgg()

    def llc3Checked(self, checked):

        if checked:
            self.llc_options["3. Skin Ulcer, Foot"][1] = 1
        else:
            self.llc_options["3. Skin Ulcer, Foot"][1] = 0
        
        self.dfFilterAndAgg()

    def llc4Checked(self, checked):

        if checked:
            self.llc_options["4. Osteomyelitis, Lower Limb"][1] = 1
        else:
            self.llc_options["4. Osteomyelitis, Lower Limb"][1] = 0
        
        self.dfFilterAndAgg()

    def llc5Checked(self, checked):

        if checked:
            self.llc_options["5. Skin Ulcer, Lower Limb"][1] = 1
        else:
            self.llc_options["5. Skin Ulcer, Lower Limb"][1] = 0
        
        self.dfFilterAndAgg()

    def llc6Checked(self, checked):

        if checked:
            self.llc_options["6. Cellulitis, Lower Limb"][1] = 1
        else:
            self.llc_options["6. Cellulitis, Lower Limb"][1] = 0
        
        self.dfFilterAndAgg()

    def llc7Checked(self, checked):

        if checked:
            self.llc_options["7. Cellulitis, Toe"][1] = 1
        else:
            self.llc_options["7. Cellulitis, Toe"][1] = 0
        
        self.dfFilterAndAgg()

    def dfFilterAndAgg(self):

        llc = []
        pad = []
        diabetes = []

        for opt in self.llc_options:
            if self.llc_options[opt][1] == 1:
                llc.append(opt)

        for opt in self.pad_options:
            if self.pad_options[opt][1] == 1:
                pad.append(opt)

        for opt in self.diabetes_options:
            if self.diabetes_options[opt][1] == 1:
                diabetes.append(opt)

        df = self.dataImport.copy()

        if len(llc) > 0:
            df = df.loc[df["psg_llc"].isin(llc)]
        if len(pad) > 0:
            df = df.loc[df["psg_pad"].isin(pad)]
        if len(diabetes) > 0:
            df = df.loc[df["psg_diabetes"].isin(diabetes)]
        if len(llc) == 0 and len(pad) == 0 and len(diabetes) == 0:
            df = df.loc[df["psg_llc"].isin(llc) & df["psg_pad"].isin(pad) & df["psg_diabetes"].isin(diabetes)]

        if df.shape[0] == 0:
            self.resultsStats = dict.fromkeys(self.resultsStats, 0)
        else:
            self.resultsStats['discharges_and_ds'] = df['discharges_and_ds'].sum()
            self.resultsStats['alos'] = df['days'].sum()/df['discharges'].sum()
            self.resultsStats['ed_v'] = df['ed_v'].sum()
            self.resultsStats['discharges_and_ds_per_pat'] = df['discharges_and_ds'].sum()/df['unique_patients_ip_ds'].sum()  
            self.resultsStats['ed_visits_per_pat'] = df['ed_v'].sum()/df['unique_patients_ed'].sum()

            if df.loc[df['hin_flag'] == 'Unique HIN'].shape[0] == 0:
                self.resultsStats['unique_patients_ip_ds'] = 0
                self.resultsStats['unique_patients_ed'] = 0
            else:
                self.resultsStats['unique_patients_ip_ds'] = df.loc[df['hin_flag'] == 'Unique HIN', 'unique_patients_ip_ds'].sum()
                self.resultsStats['unique_patients_ed'] = df.loc[df['hin_flag'] == 'Unique HIN', 'unique_patients_ed'].sum()
            
            if df['discharges_and_ds'].sum() > 0:
                self.resultsStats['major_during'] = df['major_during'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['minor_during'] = df['minor_during'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['lpr_during'] = df['lpr_during'].sum()/df['discharges_and_ds'].sum()

            if df['discharges_and_ds'].sum() > 0:
                self.resultsStats['major_1yr'] = df['major_1yr'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['minor_1yr'] = df['minor_1yr'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['lpr_1yr'] = df['lpr_1yr'].sum()/df['discharges_and_ds'].sum()

            if df['discharges_and_ds'].sum() > 0:
                self.resultsStats['major_3yr'] = df['major_3yr'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['minor_3yr'] = df['minor_3yr'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['lpr_3yr'] = df['lpr_3yr'].sum()/df['discharges_and_ds'].sum()

            if df['discharges_and_ds'].sum() > 0:
                self.resultsStats['major_5yr'] = df['major_5yr'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['minor_5yr'] = df['minor_5yr'].sum()/df['discharges_and_ds'].sum()
                self.resultsStats['lpr_5yr'] = df['lpr_5yr'].sum()/df['discharges_and_ds'].sum()

            if df['ed_v'].sum() > 0:
                self.resultsStats['major_amp_1yr'] = df['major_amp_1yr'].sum()/df['ed_v'].sum() 
                self.resultsStats['minor_amp_1yr'] = df['minor_amp_1yr'].sum()/df['ed_v'].sum() 
                self.resultsStats['lower_pr_1yr'] = df['lower_pr_1yr'].sum()/df['ed_v'].sum() 

            if df['ed_v'].sum()  > 0:
                self.resultsStats['major_amp_3yr'] = df['major_amp_3yr'].sum()/df['ed_v'].sum() 
                self.resultsStats['minor_amp_3yr'] = df['minor_amp_3yr'].sum()/df['ed_v'].sum() 
                self.resultsStats['lower_pr_3yr'] = df['lower_pr_3yr'].sum()/df['ed_v'].sum() 

            if df['ed_v'].sum() > 0:
                self.resultsStats['major_amp_5yr'] = df['major_amp_5yr'].sum()/df['ed_v'].sum() 
                self.resultsStats['minor_amp_5yr'] = df['minor_amp_5yr'].sum()/df['ed_v'].sum() 
                self.resultsStats['lower_pr_5yr'] = df['lower_pr_5yr'].sum()/df['ed_v'].sum()        

        self.updateInfoCard()

    def insert_ax(self):
        font = {
            'weight': 'normal',
            'size': 4.5
        }
        matplotlib.rc('font', **font)

        self.bar_colors = {
            'during':'#8dd3c7', 
            '1yripds': '#3182bd', '1yred': '#f03b20', 
            '3yripds': '#9ecae1', '3yred': '#feb24c', 
            '5yripds': '#deebf7', '5yred': '#ffeda0'
        }

        self.ax = self.canvas.figure.subplots(nrows=2, ncols=2) 

        self.ax[0,0].set_ylim([0, 1])
        ticks_loc = self.ax[0,0].get_yticks().tolist()
        self.ax[0,0].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[0,0].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[0,0].set_ylabel("Probability of Procedure")
        self.ax[0,0].set_title('Probability of Procedure during Discharge')

        self.ax[0,1].set_ylim([0, 1])
        ticks_loc = self.ax[0,1].get_yticks().tolist()
        self.ax[0,1].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[0,1].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[0,1].set_ylabel("Probability of Procedure")
        self.ax[0,1].set_title('Probability of Procedure Within 1YR')

        self.ax[1,0].set_ylim([0, 1])
        ticks_loc = self.ax[1,0].get_yticks().tolist()
        self.ax[1,0].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[1,0].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[1,0].set_ylabel("Probability of Procedure")
        self.ax[1,0].set_title('Probability of Procedure Within 3YRS')

        self.ax[1,1].set_ylim([0, 1])
        ticks_loc = self.ax[1,1].get_yticks().tolist()
        self.ax[1,1].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[1,1].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[1,1].set_ylabel("Probability of Procedure")
        self.ax[1,1].set_title('Probability of Procedure Within 5YRS')

        labels = ['Major\nAmputation', 'Minor\nAmputation', 'Lower\nPeripheral\nRevascularization']

        self.bar1 = self.ax[0,0].bar(labels, [0, 0, 0], color=self.bar_colors['during'])

        self.bar2_1 = self.ax[0,1].bar(labels, [0, 0, 0], color=self.bar_colors['1yripds']) 
        self.bar2_2 = self.ax[0,1].bar(labels, [0, 0, 0], color=self.bar_colors['1yred']) 

        self.bar3_1 = self.ax[1,0].bar(labels, [0, 0, 0], color=self.bar_colors['3yripds']) 
        self.bar3_2 = self.ax[1,0].bar(labels, [0, 0, 0], color=self.bar_colors['3yred'])  

        self.bar4_1 = self.ax[1,1].bar(labels, [0, 0, 0], color=self.bar_colors['5yripds'])  
        self.bar4_2 = self.ax[1,1].bar(labels, [0, 0, 0], color=self.bar_colors['5yred'])  

        self.canvas.draw()
        self.bar1 = None
        self.bar2_1 = None
        self.bar2_2 = None
        self.bar3_1 = None
        self.bar3_2 = None
        self.bar4_1 = None
        self.bar4_2 = None

    def update_chart(self):

        labels = ['Major\nAmputation', 'Minor\nAmputation', 'Lower\nPeripheral\nRevascularization']

        if self.bar1:
            self.bar1.remove()
            self.ax[0,0].cla()
        
        if self.bar2_1 and self.bar2_2:
            self.bar2_1.remove()
            self.bar2_2.remove()
            self.ax[0,1].cla()
        
        if self.bar3_1 and self.bar3_2:
            self.bar3_1.remove()
            self.bar3_2.remove()
            self.ax[1,0].cla()

        if self.bar4_1 and self.bar4_2:
            self.bar4_1.remove()
            self.bar4_2.remove()
            self.ax[1,1].cla()

        self.ax[0,0].set_title('Probability of Procedure During Discharge')
        self.ax[0,0].set_ylim([0, 1])
        ticks_loc = self.ax[0,0].get_yticks().tolist()
        self.ax[0,0].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[0,0].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[0,0].set_ylabel("Probability of Procedure")
        self.bar1 = self.ax[0,0].bar(labels, [self.resultsStats['major_during'], self.resultsStats['minor_during'], self.resultsStats['lpr_during']], color=self.bar_colors['during'])
        self.ax[0,0].bar_label(container=self.bar1, labels=["{0[major_during]:.0%}".format(self.resultsStats), "{0[minor_during]:.0%}".format(self.resultsStats), "{0[lpr_during]:.0%}".format(self.resultsStats)], padding=3)

        x = np.arange(len(labels))
        width = 0.35

        self.ax[0,1].set_title('Probability of Procedure Within 1YR')
        self.ax[0,1].set_ylim([0, 1])
        ticks_loc = self.ax[0,1].get_yticks().tolist()
        self.ax[0,1].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[0,1].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[0,1].set_ylabel("Probability of Procedure")
        self.bar2_1 = self.ax[0,1].bar(x-width/2, [self.resultsStats['major_1yr'], self.resultsStats['minor_1yr'], self.resultsStats['lpr_1yr']], color=self.bar_colors['1yripds'], label='IP & Day Surgery', width=width)
        self.bar2_2 = self.ax[0,1].bar(x+width/2, [self.resultsStats['major_amp_1yr'], self.resultsStats['minor_amp_1yr'], self.resultsStats['lower_pr_1yr']], color='#b22222', label='ED', width=width)
        self.ax[0,1].set_xticks(x)
        self.ax[0,1].set_xticklabels(labels)
        self.ax[0,1].legend()
        self.ax[0,1].bar_label(container=self.bar2_1, labels=["{0[major_1yr]:.0%}".format(self.resultsStats), "{0[minor_1yr]:.0%}".format(self.resultsStats), "{0[lpr_1yr]:.0%}".format(self.resultsStats)], padding=3)
        self.ax[0,1].bar_label(container=self.bar2_2, labels=["{0[major_amp_1yr]:.0%}".format(self.resultsStats), "{0[minor_amp_1yr]:.0%}".format(self.resultsStats), "{0[lower_pr_1yr]:.0%}".format(self.resultsStats)], padding=3)

        self.ax[1,0].set_title('Probability of Procedure Within 3YRS')
        self.ax[1,0].set_ylim([0, 1])
        ticks_loc = self.ax[1,0].get_yticks().tolist()
        self.ax[1,0].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[1,0].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[1,0].set_ylabel("Probability of Procedure")
        self.bar3_1 = self.ax[1,0].bar(x-width/2, [self.resultsStats['major_3yr'], self.resultsStats['minor_3yr'], self.resultsStats['lpr_3yr']], color=self.bar_colors['3yripds'], label='IP & Day Surgery', width=width)
        self.bar3_2 = self.ax[1,0].bar(x+width/2, [self.resultsStats['major_amp_3yr'], self.resultsStats['minor_amp_3yr'], self.resultsStats['lower_pr_3yr']], color=self.bar_colors['3yred'], label='ED', width=width)
        self.ax[1,0].set_xticks(x)
        self.ax[1,0].set_xticklabels(labels)
        self.ax[1,0].legend()
        self.ax[1,0].bar_label(container=self.bar3_1, labels=["{0[major_3yr]:.0%}".format(self.resultsStats), "{0[minor_3yr]:.0%}".format(self.resultsStats), "{0[lpr_3yr]:.0%}".format(self.resultsStats)], padding=3)
        self.ax[1,0].bar_label(container=self.bar3_2, labels=["{0[major_amp_3yr]:.0%}".format(self.resultsStats), "{0[minor_amp_3yr]:.0%}".format(self.resultsStats), "{0[lower_pr_3yr]:.0%}".format(self.resultsStats)], padding=3)

        self.ax[1,1].set_title('Probability of Procedure Within 5YRS')
        self.ax[1,1].set_ylim([0, 1])
        ticks_loc = self.ax[1,1].get_yticks().tolist()
        self.ax[1,1].yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax[1,1].set_yticklabels(['{:,.0%}'.format(x) for x in ticks_loc])
        self.ax[1,1].set_ylabel("Probability of Procedure")
        self.bar4_1 = self.ax[1,1].bar(x-width/2, [self.resultsStats['major_5yr'], self.resultsStats['minor_5yr'], self.resultsStats['lpr_5yr']], color=self.bar_colors['5yripds'], label='IP & Day Surgery', width=width)
        self.bar4_2 = self.ax[1,1].bar(x+width/2, [self.resultsStats['major_amp_5yr'], self.resultsStats['minor_amp_5yr'], self.resultsStats['lower_pr_5yr']], color=self.bar_colors['5yred'], label='ED', width=width)
        self.ax[1,1].set_xticks(x)
        self.ax[1,1].set_xticklabels(labels)
        self.ax[1,1].legend()
        self.ax[1,1].bar_label(container=self.bar4_1, labels=["{0[major_5yr]:.0%}".format(self.resultsStats), "{0[minor_5yr]:.0%}".format(self.resultsStats), "{0[lpr_5yr]:.0%}".format(self.resultsStats)], padding=3)
        self.ax[1,1].bar_label(container=self.bar4_2, labels=["{0[major_amp_5yr]:.0%}".format(self.resultsStats), "{0[minor_amp_5yr]:.0%}".format(self.resultsStats), "{0[lower_pr_5yr]:.0%}".format(self.resultsStats)], padding=3)
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = ToolWindow()
    sys.exit(app.exec_())
