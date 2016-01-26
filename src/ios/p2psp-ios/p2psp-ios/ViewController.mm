//
//  ViewController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 24/01/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "../../../core/peer_core.h"
#import <MobileVLCKit/VLCMediaPlayer.h>
#import "ViewController.h"

@interface ViewController () <VLCMediaPlayerDelegate>
@property (weak, nonatomic) IBOutlet UITextField *tfSplitterAddr;
@property (weak, nonatomic) IBOutlet UITextField *tfSplitterPort;
@property (weak, nonatomic) IBOutlet UIButton *bPlay;
@property (weak, nonatomic) IBOutlet UIView *subView;

@end

@implementation ViewController

VLCMediaPlayer *mediaPlayer;
const NSString *splitterAddr;
const NSString *splitterPort;

- (void)viewDidLoad {
  [super viewDidLoad];
  // Do any additional setup after loading the view, typically from a nib.
  
  mediaPlayer = [[VLCMediaPlayer alloc] init];
  mediaPlayer.delegate = self;
  mediaPlayer.drawable = self.subView;
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
  // Dispose of any resources that can be recreated.
}

- (IBAction)onPlay:(id)sender {
  splitterAddr = [self.tfSplitterAddr text];
  splitterPort = [self.tfSplitterPort text];
  
  dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
    const char *kSplitterAddr = splitterAddr.UTF8String;
    const char *kSplitterPort = splitterPort.UTF8String;
    
    const char *argv[] = {"p2psp", "--splitter_addr", kSplitterAddr,
      "--splitter_port", kSplitterPort};
    p2psp::run(5, argv);
  });
  
  /*dispatch_async(dispatch_get_main_queue(), ^{*/
   dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 3 * NSEC_PER_SEC), dispatch_get_main_queue(), ^{
    mediaPlayer.media = [VLCMedia mediaWithURL:[NSURL URLWithString:@"http://localhost:9999"]];
    
    [mediaPlayer play];
  });
}

@end
