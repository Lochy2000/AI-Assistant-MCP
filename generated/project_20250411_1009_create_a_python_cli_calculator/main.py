import argparse    # A standardized argument parser used by the 'argparse' package in Python Standard Library (sys) for command line interface arguments parsing  
def calculate(args):    
 if args.operation == 'add':     
  return args.x + args.y       // Addition of two numbers, x and y from user input   
 elif args.operation == 'subtract':        
  return args.x - args.y        // Substraction operation or difference between values in variables (args) for the function to subtracting second number(argv2).     
 print("Invalid Inputs")     # Invalid inputs case         
def main():   // This is our command line interface    parser = argparse.ArgumentParser()  For usage examples, you can run 'python calculator_cli.py --help' in the terminal which would show arguments needed for operation like add or subtract and values x & y from user input      def parse:
 arp (parser)           // It is used to define an argument parser   p = argparse(description="Calculate X Y operations", epilog= "Example usage... $ python calculator_cli.py  --help")       .add_argument('--operation', choices['add','subtract'], help='Select operation add or subtract')    
 parser._add_argument("-x","--variable1" ,type = int, default = 0)   // It is used to specify type of arguments and their defaults.  The 'default parameters are available in Python version >3.5      def parse:        .add_argment('y', metavar='<value>')    
 p._add__arguments(['-v','--verbosity'],type = int, choices=  range(0,21), default = 1)  // It is used to add the arguments    argparse.print_help()      sys .exit (calculate())   if __name___=='main':
 main ()     print ('Welcome')       Calculator CLI using Python: $ python calculor_cli.py --operation subtract -x5 – y3 // It will perform the operation with inputs given by user in command line interface    $python cli-calculation .add [--help] [-v / VERBOSITY ]