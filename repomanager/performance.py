import pandas as pd

def calculate_accuracy(tp, fp, tn, fn):
    """Calculate accuracy """
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    return accuracy

def calculate_precision(tp, fp):
    """Calculate precision """
    precision = tp / (tp + fp)
    return precision

def calculate_recall(tp,fn):
    """Calculate recall """
    recall = tp / (tp + fn)
    return recall

def calculate_f1_score(tp, fp,fn):
    """Calculate F1-score """
    precision = calculate_precision(tp, fp)
    recall = calculate_recall(tp, fn)
    f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score

if __name__ == "__main__":
    confusion_matrix = pd.read_csv("./repomanager/cm-output data.csv")
    #confusion_matrix = pd.read_csv("./repomanager/cm-param tinkering.csv")
    tp = confusion_matrix.iloc[0, 1]
    fn = confusion_matrix.iloc[0, 2]
    fp = confusion_matrix.iloc[1, 1]
    tn = confusion_matrix.iloc[1, 2]
    accuracy = calculate_accuracy(tp, fp, tn, fn)
    precision = calculate_precision(tp, fp)
    recall = calculate_recall(tp, fn)
    f1_score = calculate_f1_score(tp, fp, fn)
    

    print(f"accuracy: {accuracy}")
    print(f"precision: {precision}")
    print(f"recall: {recall}")
    print(f"f1: {f1_score}")


