from django.conf import settings
from django.shortcuts import render
import joblib
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from django.contrib import messages
from users.models import UserRegistrationModel
from .models import UserRegistrationModel

# Set up a non-interactive backend for matplotlib
matplotlib.use('Agg')

def training(request):
    # Load your dataset
    new_df = pd.read_csv(r'media\final_balanced_dataset.csv')

    # Split features and target
    x = new_df.drop('Attrition', axis=1)
    y = new_df['Attrition']

    # Split the data into training and testing sets
    from sklearn.model_selection import train_test_split
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Train the Random Forest Classifier
    rf = RandomForestClassifier()
    rf.fit(x_train, y_train)

    # Save the model
    joblib.dump(rf, r'media\rf_model.pkl')

    # Make predictions
    y_pred = rf.predict(x_test)

    # Generate reports and metrics
    report = classification_report(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Display the confusion matrix
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['No Attrition', 'Attrition'], yticklabels=['No Attrition', 'Attrition'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(r'media\confusion_matrix.png')  # Save the figure
    plt.close()  # Close the plot

    context = { 
        'acc': acc,
        'report': report,
        'confusion_matrix_image': 'media/confusion_matrix.png'  # Path to save for rendering in template
    }
    return render(request, 'users/accuracy.html', context)

def prediction(request):
    # Path to the saved model
    model_path = r'media\rf_model.pkl'

    # Load the pre-trained model
    if os.path.exists(model_path):
        rf = joblib.load(model_path)
    else:
        return render(request, 'users/prediction.html', {'error': 'Model file not found. Please train the model first.'})

    if request.method == 'POST':
        try:
            # Extract features from the form input
            features = [
                float(request.POST['Age']),
                float(request.POST['JobLevel']),
                float(request.POST['MaritalStatus']),
                float(request.POST['MonthlyIncome']),
                float(request.POST['OverTime']),
                float(request.POST['StockOptionLevel']),
                float(request.POST['TotalWorkingYears']),
                float(request.POST['YearsAtCompany']),
                float(request.POST['YearsInCurrentRole']),
                float(request.POST['YearsWithCurrManager']),
            ]

            # Reshape features for prediction
            input_features = [features]
            prediction = rf.predict(input_features)

            # Determine predicted result
            result = "Attrition" if prediction[0] == 1 else "No Attrition"

            context = {'prediction': result}
            return render(request, 'users/detection.html', context)

        except KeyError as e:
            return render(request, 'users/prediction.html', {'error': f'Missing input data: {e}'})

        except ValueError as e:
            return render(request, 'users/prediction.html', {'error': f'Invalid input data: {e}'})

    return render(request, 'users/prediction.html')





def ViewDataset(request):
    dataset = os.path.join(settings.MEDIA_ROOT, 'final_balanced_dataset.csv')
    import pandas as pd
    df = pd.read_csv(dataset, nrows=100)
    df = df.to_html(index=None)
    return render(request, 'users/viewData.html', {'data': df})


from django.shortcuts import render, redirect
from .models import UserRegistrationModel
from django.contrib import messages

def UserRegisterActions(request):
    if request.method == 'POST':
        user = UserRegistrationModel(
            name=request.POST['name'],
            loginid=request.POST['loginid'],
            password=request.POST['password'],
            mobile=request.POST['mobile'],
            email=request.POST['email'],
            locality=request.POST['locality'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            status='waiting'
        )
        user.save()
        messages.success(request,"Registration successful!")
    return render(request, 'UserRegistrations.html') 


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                data = {'loginid': loginid}
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


def index(request):
    return render(request,"index.html")