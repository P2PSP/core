//
//  Channel.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 19/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "Channel.h"

@implementation Channel

/**
 *  Initializes a channel
 *
 *  @param title The title of the channel
 *  @param ip    The ip of the channel
 *  @param port  The port of the channel
 *
 *  @return The initialized object
 */
- (instancetype)init:(NSString*)title
     withDescription:(NSString*)description
              withIP:(NSString*)ip
            withPort:(NSString*)port {
  self = [super init];
  if (self) {
    self.title = title;
    self.ip = ip;
    self.port = port;
    self.desc = description;
  }
  return self;
}

@end
