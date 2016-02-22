//
//  ChannelsController.h
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 19/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "BocastClient.h"
#import "Channel.h"
#import "PlayerController.h"

@interface ChannelsController : UIViewController<BocastClientDelegate>

- (IBAction)onGetChannels:(id)sender;
- (IBAction)unwindToChannels:(UIStoryboardSegue *)unwindSegue;
- (IBAction)onKeyboardDismiss:(id)sender;

@end
