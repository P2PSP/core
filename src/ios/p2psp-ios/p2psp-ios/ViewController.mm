//
//  ViewController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 24/01/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import <MobileVLCKit/VLCMediaPlayer.h>
#import "../../../core/peer_core.h"
#import "ViewController.h"

@interface ViewController ()<VLCMediaPlayerDelegate>
@property(weak, nonatomic) IBOutlet UITextField *tfSplitterAddr;
@property(weak, nonatomic) IBOutlet UITextField *tfSplitterPort;
@property(weak, nonatomic) IBOutlet UIButton *bPlay;
@property(weak, nonatomic) IBOutlet UIButton *bStop;
@property(weak, nonatomic) IBOutlet UIView *subView;
@property(nonatomic) BOOL playing;
@property(weak, nonatomic) IBOutlet UIButton *bFullscreen;
@property(weak, nonatomic) IBOutlet UIView *controlsSubView;
@property(weak, nonatomic) IBOutlet UIView *videoSubView;

@end

@implementation ViewController

VLCMediaPlayer *mediaPlayer;
const NSString *splitterAddr;
const NSString *splitterPort;
NSString *const kPlayerEndpoint = @"http://localhost:9999";

- (void)viewDidLoad {
  [super viewDidLoad];
  // Do any additional setup after loading the view, typically from a nib.

  self.controlsSubView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin;

  mediaPlayer = [[VLCMediaPlayer alloc] init];
  mediaPlayer.delegate = self;
  mediaPlayer.drawable = self.videoSubView;
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
  // Dispose of any resources that can be recreated.
}

/**
 *  Callback function that listens to bPlay button
 *
 *  @param sender The pressed button
 */
- (IBAction)onPlay:(id)sender {
  if (self.playing) {
    return;
  }
  self.playing = true;

  splitterAddr = [self.tfSplitterAddr text];
  splitterPort = [self.tfSplitterPort text];

  // Runs into a different asyncrhonous thread to avoid UI blocking.
  dispatch_async(
      dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        const char *kSplitterAddr = splitterAddr.UTF8String;
        const char *kSplitterPort = splitterPort.UTF8String;

        const char *argv[] = {"p2psp", "--splitter_addr", kSplitterAddr,
                              "--splitter_port", kSplitterPort};
        p2psp::run(5, argv);
      });

  // Launch the viewer
  mediaPlayer.media =
      [VLCMedia mediaWithURL:[NSURL URLWithString:kPlayerEndpoint]];

  [mediaPlayer play];

  // Release focus from textfields
  [self.tfSplitterAddr resignFirstResponder];
  [self.tfSplitterPort resignFirstResponder];
}

/**
 *  Callback function that listens to bStop button
 *
 *  @param sender The pressed button
 */
- (IBAction)onStop:(id)sender {
  if (!self.playing) {
    return;
  }
  self.playing = false;

  // The peer_core thread finishes when the viewer disconnects from it
  [mediaPlayer stop];

  // Release focus from textfields
  [self.tfSplitterAddr resignFirstResponder];
  [self.tfSplitterPort resignFirstResponder];

  // If orientation is lanscape when the video stops, set orientation to
  // portrait
  if (UIDeviceOrientationIsLandscape([[UIDevice currentDevice] orientation])) {
    [self
        setOrientation:[NSNumber numberWithInt:UIInterfaceOrientationPortrait]];
  }
}

- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event {
  UITouch *touch = [[event allTouches] anyObject];
  if ([self.tfSplitterAddr isFirstResponder] &&
      [touch view] != self.tfSplitterAddr) {
    [self.tfSplitterAddr resignFirstResponder];
  } else if ([self.tfSplitterPort isFirstResponder] &&
             [touch view] != self.tfSplitterPort) {
    [self.tfSplitterPort resignFirstResponder];
  }

  [super touchesBegan:touches withEvent:event];
}

- (IBAction)onFullscreen:(id)sender {
  UIDeviceOrientation currentOrientation =
      [[UIDevice currentDevice] orientation];

  // Portrait as default
  NSNumber *orientation =
      [NSNumber numberWithInt:UIInterfaceOrientationPortrait];

  // If portrait, change to landscape
  if (UIDeviceOrientationIsPortrait(currentOrientation)) {
    orientation = [NSNumber numberWithInt:UIInterfaceOrientationLandscapeLeft];
  }

  [self setOrientation:orientation];
  // [[UIDevice currentDevice] setValue:orientation forKey:@"orientation"];
}

- (UIStatusBarStyle)preferredStatusBarStyle {
  return UIStatusBarStyleLightContent;
}

- (void)setOrientation:(NSNumber *)orientation {
  [[UIDevice currentDevice] setValue:orientation forKey:@"orientation"];
}

@end
