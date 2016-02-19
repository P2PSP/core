//
//  ChannelsController.h
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 19/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "Channel.h"

@interface ChannelsController
    : UIViewController<UITableViewDataSource, UITableViewDelegate>

@property(nonatomic) NSMutableArray<Channel *> *channelsList;

@property(weak, nonatomic) IBOutlet UITableView *tvChannelsList;

- (IBAction)onGetChannels:(id)sender;

@end
