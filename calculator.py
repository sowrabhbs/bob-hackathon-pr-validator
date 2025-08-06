#!/usr/bin/env python3
"""
A simple calculator script for the Bob Hackathon repository.
"""

def add(a, b):
    """Add two numbers and return the result."""
    return a + b

def subtract(a, b):
    """Subtract b from a and return the result."""
    return a - b

def multiply(a, b):
    """Multiply two numbers and return the result."""
    return a * b

def divide(a, b):
    """Divide a by b and return the result."""
    if b == 0:
        return "Error: Division by zero"
    return a / b

def main():
    """Main function that demonstrates the calculator functionality."""
    print("Welcome to the Bob Hackathon Calculator!")
    print("Available operations:")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    
    try:
        choice = int(input("Enter choice (1-4): "))
        if choice < 1 or choice > 4:
            print("Invalid choice")
            return
            
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        
        if choice == 1:
            print(f"{num1} + {num2} = {add(num1, num2)}")
        elif choice == 2:
            print(f"{num1} - {num2} = {subtract(num1, num2)}")
        elif choice == 3:
            print(f"{num1} * {num2} = {multiply(num1, num2)}")
        elif choice == 4:
            print(f"{num1} / {num2} = {divide(num1, num2)}")
            
    except ValueError:
        print("Error: Please enter valid numbers")

if __name__ == "__main__":
    main()

# Made with Bob
