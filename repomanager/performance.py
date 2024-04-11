def calculate_accuracy(tp, fp, tn, fn):
    """Calculate accuracy """
    return (tp + tn) / (tp + tn + fp + fn)

def calculate_precision(tp, fp):
    """Calculate precision """
    return tp / (tp + fp)

def calculate_recall(tp,fn):
    """Calculate recall """
    return tp / (tp + fn)

def calculate_f1_score(tp, fp,fn):
    """Calculate F1-score """
    precision = calculate_precision(tp, fp)
    recall = calculate_recall(tp, fn)
    return 2 * (precision * recall) / (precision + recall)

