//
//  ViewController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 24/01/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "../../../core/peer_core.h"
#import "ViewController.h"

@interface ViewController ()
@property(weak, nonatomic) IBOutlet UITextField *tfSplitterAddr;
@property(weak, nonatomic) IBOutlet UITextField *tfSplitterPort;
@property(weak, nonatomic) IBOutlet UIButton *bPlay;

@end

@implementation ViewController

const NSString *splitterAddr;
const NSString *splitterPort;

- (void)viewDidLoad {
  [super viewDidLoad];
  // Do any additional setup after loading the view, typically from a nib.
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
  // Dispose of any resources that can be recreated.
}
- (IBAction)onPlay:(id)sender {
  splitterAddr = [self.tfSplitterAddr text];
  splitterPort = [self.tfSplitterPort text];

  dispatch_async(dispatch_get_main_queue(), ^{
    const char *kSplitterAddr = splitterAddr.UTF8String;
    const char *kSplitterPort = splitterPort.UTF8String;
    
    const char *argv[] = {"p2psp", "--splitter_addr", kSplitterAddr,
                          "--splitter_port", kSplitterPort};
    p2psp::run(5, argv);
  });
}

@end
