//
//  ViewController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 24/01/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "ViewController.h"
#import "../../../core/peer_core.h"
#import <MobileVLCKit/VLCMediaPlayer.h>

@interface ViewController () <VLCMediaPlayerDelegate>
@property (weak, nonatomic) IBOutlet UITextField *tvSplitterAddr;
@property (weak, nonatomic) IBOutlet UITextField *tfSpliiterPort;
@property (weak, nonatomic) IBOutlet UIButton *bPlay;
@property (weak, nonatomic) IBOutlet UIView *subView;

@end

@implementation ViewController

VLCMediaPlayer *mediaPlayer;

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
  NSString *url = self.tvSplitterAddr.text;
  NSString *port = self.tfSpliiterPort.text;
  
  mediaPlayer.media = [VLCMedia mediaWithURL:[NSURL URLWithString:[NSString stringWithFormat:@"%@:%@", url, port]]];
  
  [mediaPlayer play];
}

@end
