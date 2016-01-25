//
//  ViewController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 24/01/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "ViewController.h"
#import "../../../core/peer_core.h"

@interface ViewController ()
@property (weak, nonatomic) IBOutlet UITextField *tvSplitterAddr;
@property (weak, nonatomic) IBOutlet UITextField *tfSpliiterPort;
@property (weak, nonatomic) IBOutlet UIButton *bPlay;

@end

@implementation ViewController

- (void)viewDidLoad {
  [super viewDidLoad];
  // Do any additional setup after loading the view, typically from a nib.
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
  // Dispose of any resources that can be recreated.
}
- (IBAction)onPlay:(id)sender {
}

@end
