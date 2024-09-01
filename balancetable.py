import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

# Function to calculate means, SDs, and differences
def balance_summary(var, data, treatment_var):
    summary_df = data.groupby(treatment_var).agg(
        n=(var, 'count'),
        mean=(var, 'mean'),
        sd=(var, lambda x: np.std(x, ddof=0))
    ).reset_index()
    
    diff = summary_df['mean'].diff().iloc[-1]
    
    return summary_df


def multi_treat_var_balance_table_latex(data, treatment, covariates, thresholds=[0.1, 0.05, 0.01]):    
    DataList = []
    for var in covariates:
        table_trial = balance_summary(var, data, treatment)
        table_trial = table_trial.set_index(treatment)
        df = table_trial[table_trial.columns].T
        data_dict = df.to_dict()
        DataList.append({'Variable':var, 'stats':data_dict})
    
    # Calculate the observation count for each combination of R1Treatment, R2Treatment, and TreatmentType
    obv_counts = data.groupby(treatment).size().reset_index(name='Count')
    obv_counts = obv_counts.set_index(treatment)
    obv_counts = obv_counts.to_dict()['Count']
    VariableList = [x['Variable'] for x in DataList]
    Headers = [x[:3] for x in list(DataList[0]['stats'].keys())]
    Headers = ['all'] + Headers
    
    col_number = len(Headers)+1
    c_string = 'c'*col_number
    
    TableHeader = "\\begin{tabular}{@{\extracolsep{5pt}}l"+c_string+"}\n"+"\\\[-1.8ex]\hline\n"+"\hline \\\[-1.8ex]\n"
    
    HeaderSep = " & \multicolumn{"+str(col_number)+"}{c}{\\textit{Data Groups:}} \\\ " + "\n\cline{2-"+str(col_number+1)+"}"
    
    VarHeader = "\Variables & "
    
    SimplificationMap = {'Fully Abstract':'FA',
                        'Fully Figurative':'FF',
                        'Semi Abstract':'SA'}
    
    for i in range(len(Headers)):
        var = Headers[i]
        if var == 'all':
            var_head = 'AllData'
            VarHeader = VarHeader + "\multicolumn{1}{c}{"+var_head+"} &"
        elif i != len(Headers) -1:
            var_head = ''
            for i in len(var):
                var_head = var_head + var[i] + ' '
            VarHeader = VarHeader + "\multicolumn{1}{c}{"+var_head+"} &"
        else:
            var_head = ''
            for i in len(var):
                var_head = var_head + var[i] + ' '
            VarHeader = VarHeader + "\multicolumn{1}{c}{"+var_head+"} \\\ \n"
    VarHeader = VarHeader + '\hline \\\[-1.8ex]\n'
    
    
    VarBody = ""
    
    Grouped_Data = data.groupby(treatment)
    
    for i in range(len(VariableList)):
        test_var = VariableList[i]
        Data = DataList[i]['stats']
        population = data[test_var].to_list()
        VarRow = test_var.replace('_', ' ') + " & "
        for group in Headers:
            if group == 'all':
                mean = data[test_var].mean()
                numerical_val = f"{mean:.3f}"
                VarRow = VarRow + numerical_val + " & "
            else:
                group_data = Grouped_Data.get_group(group)
                subpopulation = group_data[test_var].to_list()
                test_result = ttest_ind(subpopulation, population)
                indexer = group
                mean = Data[indexer]['mean']
                if test_result.pvalue <= thresholds[2]:
                    numerical_val = f"${mean:.3f}"+"^{***}$"
                elif test_result.pvalue <= thresholds[1]:
                    numerical_val = f"${mean:.3f}"+"^{**}$"
                elif test_result.pvalue <= thresholds[0]:
                    numerical_val = f"${mean:.3f}"+"^{*}$"
                else:
                    numerical_val = f"{mean:.3f}"
                if group != Headers[-1]:
                    VarRow = VarRow + numerical_val + " & "
                else:
                    VarRow = VarRow + numerical_val + " \\\ \n"
        
        VarRow = VarRow + " & "
        for group in Headers:
            indexer = group
            if group == 'all':
                sd = data[test_var].std()
                VarRow = VarRow + f"({sd:.3f})" + " & "
            else:
                sd = Data[indexer]['sd']
                if group != Headers[-1]:
                    VarRow = VarRow + f"({sd:.3f})" + " & "
                else:
                    VarRow = VarRow + f"({sd:.3f})" + " \\\ \n"
    
        EndRow = ' & '*col_number+"\\\ \n"
        VarRow = VarRow + EndRow
        VarBody = VarBody+VarRow
    VarBody = VarBody + "\hline \\\[-1.8ex]\n"
    EndCount = "Observations & "
    
    for group in Headers:
        if group == 'all':
            obv_num = data.shape[0]
            EndCount = EndCount + str(int(obv_num)) + " & "
        else:
            obv_num = obv_counts[group]
            if group != Headers[-1]:
                EndCount = EndCount + str(int(obv_num)) + " & "
            else:
                EndCount = EndCount + str(int(obv_num)) + "\\\ \n"
    EndFooter = "\hline\n" + "\hline \\\[-1.8ex]\n" 
    
    NoteFooter = f"\\multicolumn{{{col_number-4}}}{{r}}{{\textit{{Note:}}}}  & \\multicolumn{{4}}{{r}}{{\\textsuperscript{{*}}p$<${thresholds[0]:.2f}; \\textsuperscript{{**}}p$<${thresholds[1]:.2f}; \\textsuperscript{{***}}p$<${thresholds[2]:.2f}}} \\\ \n"
    
    Table = TableHeader+HeaderSep+VarHeader+VarBody+EndCount+EndFooter + NoteFooter + "\end{tabular} "
    return Table




def single_treat_var_balance_table_latex(data, treatment, covariates, thresholds=[0.1, 0.05, 0.01]):    
    DataList = []
    for var in covariates:
        table_trial = balance_summary(var, data, treatment)
        table_trial = table_trial.set_index(treatment)
        df = table_trial[table_trial.columns].T
        data_dict = df.to_dict()
        DataList.append({'Variable':var, 'stats':data_dict})
    
    # Calculate the observation count for each TreatmentType
    obv_counts = data.groupby(treatment).size().reset_index(name='Count')
    obv_counts = obv_counts.set_index(treatment)
    obv_counts = obv_counts.to_dict()['Count']
    VariableList = [x['Variable'] for x in DataList]
    Headers = [x for x in list(DataList[0]['stats'].keys())]
    Headers = ['all'] + Headers
    
    col_number = len(Headers)+1
    c_string = 'c'*col_number
    
    TableHeader = "\\begin{tabular}{@{\extracolsep{5pt}}l"+c_string+"}\n"+"\\\[-1.8ex]\hline\n"+"\hline \\\[-1.8ex]\n"
    
    HeaderSep = " & \multicolumn{"+str(col_number)+"}{c}{\\textit{Data Groups:}} \\\ " + "\n\cline{2-"+str(col_number+1)+"}"
    
    VarHeader = "\Variables & "
    
    for i in range(len(Headers)):
        var = Headers[i]
        if var == 'all':
            var_head = 'AllData'
            VarHeader = VarHeader + "\multicolumn{1}{c}{"+var_head+"} &"
        elif i != len(Headers) -1:
            var_head = var
            VarHeader = VarHeader + "\multicolumn{1}{c}{"+var_head+"} &"
        else:
            var_head = var
            VarHeader = VarHeader + "\multicolumn{1}{c}{"+var_head+"} \\\ \n"
    VarHeader = VarHeader + '\hline \\\[-1.8ex]\n'
    
    
    VarBody = ""
    
    Grouped_Data = data.groupby(treatment)
    
    for i in range(len(VariableList)):
        test_var = VariableList[i]
        Data = DataList[i]['stats']
        population = data[test_var].to_list()
        VarRow = test_var.replace('_', ' ') + " & "
        for group in Headers:
            if group == 'all':
                mean = data[test_var].mean()
                numerical_val = f"{mean:.3f}"
                VarRow = VarRow + numerical_val + " & "
            else:
                group_data = Grouped_Data.get_group(group)
                mean = Data[group]['mean']
                subpopulation = group_data[test_var].to_list()
                test_result = ttest_ind(subpopulation, population)
                if test_result.pvalue <= thresholds[2]:
                    numerical_val = f"${mean:.3f}"+"^{***}$"
                elif test_result.pvalue <= thresholds[1]:
                    numerical_val = f"${mean:.3f}"+"^{**}$"
                elif test_result.pvalue <= thresholds[0]:
                    numerical_val = f"${mean:.3f}"+"^{*}$"
                else:
                    numerical_val = f"{mean:.3f}"
                indexer = group
                if group != Headers[-1]:
                    VarRow = VarRow + numerical_val + " & "
                else:
                    VarRow = VarRow + numerical_val + " \\\ \n"
        
        VarRow = VarRow + " & "
        for group in Headers:
            indexer = group
            if group == 'all':
                sd = data[test_var].std()
                VarRow = VarRow + f"({sd:.3f})" + " & "
            else:
                sd = Data[indexer]['sd']
                if group != Headers[-1]:
                    VarRow = VarRow + f"({sd:.3f})" + " & "
                else:
                    VarRow = VarRow + f"({sd:.3f})" + " \\\ \n"
    
        EndRow = ' & '*col_number+"\\\ \n"
        VarRow = VarRow + EndRow
        VarBody = VarBody+VarRow
    VarBody = VarBody + "\hline \\\[-1.8ex]\n"
    EndCount = "Observations & "
    
    for group in Headers:
        if group == 'all':
            obv_num = data.shape[0]
            EndCount = EndCount + str(int(obv_num)) + " & "
        else:
            obv_num = obv_counts[group]
            if group != Headers[-1]:
                EndCount = EndCount + str(int(obv_num)) + " & "
            else:
                EndCount = EndCount + str(int(obv_num)) + "\\\ \n"
    EndFooter = "\hline\n" + "\hline \\\[-1.8ex]\n" 
    
    NoteFooter = f"\\multicolumn{{{col_number-4}}}{{r}}{{\textit{{Note:}}}}  & \\multicolumn{{4}}{{r}}{{\\textsuperscript{{*}}p$<${thresholds[0]:.2f}; \\textsuperscript{{**}}p$<${thresholds[1]:.2f}; \\textsuperscript{{***}}p$<${thresholds[2]:.2f}}} \\\ \n"
    
    Table = TableHeader+HeaderSep+VarHeader+VarBody+EndCount+EndFooter + NoteFooter + "\end{tabular} "
    return Table
