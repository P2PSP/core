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
@property(strong, nonatomic) IBOutlet UIView *mainView;
@property(weak, nonatomic) IBOutlet UITextField *tfSplitterAddr;
@property(weak, nonatomic) IBOutlet UITextField *tfSplitterPort;
@property(weak, nonatomic) IBOutlet UIButton *bPlay;
@property(weak, nonatomic) IBOutlet UIButton *bStop;
@property(weak, nonatomic) IBOutlet UIView *playerContainer;
@property(nonatomic) BOOL playing;
@property(weak, nonatomic) IBOutlet UIButton *bFullscreen;
@property(weak, nonatomic) IBOutlet UIView *controlsSubView;
@property(weak, nonatomic) IBOutlet UIView *videoSubView;
@property(weak, nonatomic)
    IBOutlet NSLayoutConstraint *playerContainterHeightConstraint;

@end

@implementation ViewController

VLCMediaPlayer *mediaPlayer;
const NSString *splitterAddr;
const NSString *splitterPort;
NSString *const kPlayerEndpoint = @"http://localhost:9999";
CGRect playerContainerFrame;
BOOL isFullScreen = NO;

- (void)viewDidLoad {
  [super viewDidLoad];
  // Do any additional setup after loading the view, typically from a nib.

  [self.mainView addSubview:self.playerContainer];

  mediaPlayer = [[VLCMediaPlayer alloc] initWithOptions:@[ @"--extraintf=" ]];
  mediaPlayer.delegate = self;
  mediaPlayer.drawable = self.videoSubView;

  [[UIDevice currentDevice] beginGeneratingDeviceOrientationNotifications];
  [[NSNotificationCenter defaultCenter]
      addObserver:self
         selector:@selector(orientationChanged:)
             name:UIDeviceOrientationDidChangeNotification
           object:[UIDevice currentDevice]];
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

        try {
          p2psp::run(5, argv);
        } catch (boost::system::system_error e) {
          self.playing = false;
          if (IFF_DEBUG) {
            LOG(e.what());
          }
          [self
              displayAlertView:[[NSString alloc] initWithUTF8String:e.what()]];
        }

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

/**
 *  Sets the player view to fullscreen
 *
 *  @param sender The button
 */
- (IBAction)onFullscreen:(id)sender {
  CGRect screenBounds = [UIApplication sharedApplication].keyWindow.bounds;

  NSInteger playerHeight = self.playerContainer.frame.size.height;
  NSInteger screenHeight = screenBounds.size.height;

  // The constraint value is the diference between the screen's height and
  // view's height
  self.playerContainterHeightConstraint.constant = screenHeight - playerHeight;

  isFullScreen = !isFullScreen;

  [self.playerContainer layoutIfNeeded];

  // The constraint value is the diference between the screen's height and
  // view's height

  [self.view layoutIfNeeded];

  [UIView animateWithDuration:0.2
                   animations:^{
                     self.playerContainterHeightConstraint.constant =
                         screenHeight - playerHeight;
                     [self.view layoutIfNeeded];
                   }];
}

- (void)displayAlertView:(NSString *)message {
  dispatch_async(dispatch_get_main_queue(), ^{
    UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error"
                                                    message:message
                                                   delegate:self
                                          cancelButtonTitle:@"OK"
                                          otherButtonTitles:nil];
    [alert show];
  });
}

- (UIStatusBarStyle)preferredStatusBarStyle {
  return UIStatusBarStyleLightContent;
}

- (void)setOrientation:(NSNumber *)orientation {
  [[UIDevice currentDevice] setValue:orientation forKey:@"orientation"];
}

- (void)adjustVideo:(UIDeviceOrientation)orientation {
  CGRect screenBounds = [UIApplication sharedApplication].keyWindow.bounds;
  NSInteger playerHeight = self.playerContainer.frame.size.height;
  NSInteger screenHeight = screenBounds.size.height;

  // The constraint value is the diference between the screen's height and
  // view's height minus the previous height constraint
  switch (orientation) {
    case UIDeviceOrientationPortrait:
      self.playerContainterHeightConstraint.constant =
          screenHeight -
          (playerHeight - self.playerContainterHeightConstraint.constant);
      break;
    case UIDeviceOrientationLandscapeLeft:
      self.playerContainterHeightConstraint.constant =
          screenHeight -
          (playerHeight - self.playerContainterHeightConstraint.constant);
      break;
    default:
      break;
  }
}

- (void)orientationChanged:(NSNotification *)note {
  UIDevice *device = note.object;
  switch (device.orientation) {
    case UIDeviceOrientationPortrait:
      if (isFullScreen) {
        [self adjustVideo:UIDeviceOrientationPortrait];
      }
      break;
    case UIDeviceOrientationLandscapeRight:
    case UIDeviceOrientationLandscapeLeft:
      if (isFullScreen) {
        [self adjustVideo:UIDeviceOrientationLandscapeLeft];
      }
      break;
    default:
      break;
  };
}

@end
