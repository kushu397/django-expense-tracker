
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import login

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.db.models import Sum

from .forms import UserRegisterForm, ExpenseForm

from .models import Expense, Category, ExpenseItem

# ==========================================
# REGISTER
# ==========================================

def register(request):

    if request.method == 'POST':

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            # Create default categories and items for new user

            default_categories = {
                'Food': [
                    'Rice',
                    'Bread',
                    'Fruits',
                    'Vegetables',
                    'Momo'
                ],

                'Transport': [
                    'Bus',
                    'Taxi',
                    'Bike',
                    'Fuel'
                ],

                'Entertainment': [
                    'Movie',
                    'Games',
                    'Concert'
                ],

                'Utilities': [
                    'Electricity',
                    'Water',
                    'Internet',
                    'Mobile Recharge'
                ],

                'Other': [
                    'Shopping',
                    'Personal',
                    'Other'
                ]
            }


            for category_name, item_names in default_categories.items():

                category = Category.objects.create(
                    name=category_name,
                    user=user
                )

                for item_name in item_names:

                    ExpenseItem.objects.create(
                        category=category,
                        name=item_name
                    )

            # Automatically login user
            login(request, user)

            messages.success(
                request,
                f'Account created successfully! Welcome, {user.username}!'
            )

            return redirect('dashboard')

    else:

        form = UserRegisterForm()

    return render(
        request,
        'tracker/register.html',
        {'form': form}
    )


# ==========================================
# DASHBOARD
# ==========================================

@login_required
def dashboard(request):

    # --------------------------------------
    # CREATE DEFAULT ITEMS FOR EXISTING USER
    # --------------------------------------

    default_items = {
        'Food': [
            'Rice',
            'Bread',
            'Fruits',
            'Vegetables',
            'Momo'
        ],

        'Transport': [
            'Bus',
            'Taxi',
            'Bike',
            'Fuel'
        ],

        'Entertainment': [
            'Movie',
            'Games',
            'Concert'
        ],

        'Utilities': [
            'Electricity',
            'Water',
            'Internet',
            'Mobile Recharge'
        ],

        'Other': [
            'Shopping',
            'Personal',
            'Other'
        ]
    }


    for category_name, item_names in default_items.items():

        category = Category.objects.filter(
            name=category_name,
            user=request.user
        ).first()

        if category:

            for item_name in item_names:

                ExpenseItem.objects.get_or_create(
                    category=category,
                    name=item_name
                )


    # --------------------------------------
    # GET ALL EXPENSES FOR CURRENT USER
    # --------------------------------------

    expenses = Expense.objects.filter(
        user=request.user
    ).select_related(
        'category'
    ).order_by('-date')


    # --------------------------------------
    # GET FILTER VALUES
    # --------------------------------------

    selected_month = request.GET.get(
        'month',
        ''
    )

    selected_category = request.GET.get(
        'category',
        ''
    )

    start_date = request.GET.get(
        'start_date',
        ''
    )

    end_date = request.GET.get(
        'end_date',
        ''
    )


    # --------------------------------------
    # MONTH FILTER
    # --------------------------------------

    if selected_month:

        expenses = expenses.filter(
            date__month=selected_month
        )


    # --------------------------------------
    # CATEGORY FILTER
    # --------------------------------------

    if selected_category:

        expenses = expenses.filter(
            category__name=selected_category
        )


    # --------------------------------------
    # START DATE FILTER
    # --------------------------------------

    if start_date:

        expenses = expenses.filter(
            date__gte=start_date
        )


    # --------------------------------------
    # END DATE FILTER
    # --------------------------------------

    if end_date:

        expenses = expenses.filter(
            date__lte=end_date
        )


    # --------------------------------------
    # TOTAL EXPENSE
    # --------------------------------------

    total_expense = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0


    # --------------------------------------
    # GET USER'S CATEGORIES
    # --------------------------------------

    categories = Category.objects.filter(
        user=request.user
    ).order_by('name')


    # --------------------------------------
    # CATEGORY-WISE EXPENSES
    # --------------------------------------

    category_data = {}

    for expense in expenses:

        # Check if expense has a category
        if expense.category:

            category_name = expense.category.name

        else:

            category_name = 'Uncategorized'


        # Create category if not already present
        if category_name not in category_data:

            category_data[category_name] = {
                'items': [],
                'total': 0
            }


        # Add expense/item
        category_data[category_name]['items'].append(
            expense
        )


        # Add amount to category total
        category_data[category_name]['total'] += expense.amount


    # --------------------------------------
    # CATEGORY SUMMARY
    # Used by dashboard.html
    # --------------------------------------

    category_summary = []

    for category_name, data in category_data.items():

        category_summary.append({
            'category__name': category_name,
            'total': data['total']
        })


    # --------------------------------------
    # MONTHS
    # --------------------------------------

    months = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]


    # --------------------------------------
    # CONTEXT
    # --------------------------------------

    context = {

        'expenses': expenses,

        'total_expense': total_expense,

        'categories': categories,

        'category_data': category_data,

        'category_summary': category_summary,

        'months': months,

        'selected_month': selected_month,

        'selected_category': selected_category,

        'start_date': start_date,

        'end_date': end_date,

    }


    # --------------------------------------
    # RETURN DASHBOARD
    # --------------------------------------

    return render(
        request,
        'tracker/dashboard.html',
        context
    )


# ==========================================
# ADD EXPENSE
# ==========================================

@login_required
def add_expense(request):

    if request.method == 'POST':

        form = ExpenseForm(
            request.POST,
            user=request.user
            

    
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.user = request.user

            expense.save()

            messages.success(
                request,
                'Expense added successfully!'
            )

            return redirect('dashboard')

    else:

        form = ExpenseForm(
            user=request.user
        )


    return render(
        request,
        'tracker/add_expense.html',
        {'form': form}
    )


# ==========================================
# EDIT EXPENSE
# ==========================================

@login_required
def edit_expense(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user
    )


    if request.method == 'POST':

        form = ExpenseForm(
            request.POST,
            instance=expense,
            user=request.user
        )


        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Expense updated successfully!'
            )

            return redirect('dashboard')

    else:

        form = ExpenseForm(
            instance=expense,
            user=request.user
        )


    return render(
        request,
        'tracker/edit_expense.html',
        {
            'form': form,
            'expense': expense
        }
    )


# ==========================================
# DELETE EXPENSE
# ==========================================

@login_required
def delete_expense(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user
    )


    if request.method == 'POST':

        expense.delete()

        messages.success(
            request,
            'Expense deleted successfully!'
        )

        return redirect('dashboard')


    return render(
        request,
        'tracker/delete_expense.html',
        {
            'expense': expense
        }
    )

