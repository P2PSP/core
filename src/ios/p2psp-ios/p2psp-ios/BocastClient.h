//
//  BocastClient.h
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 22/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "Channel.h"

@interface BocastClient : NSObject

@property(nonatomic) NSURL* bocastURL;

- (instancetype)initWithString:(NSString*)urlString;

/**
 *  Makes an http request to the server to get the channels list
 */
- (void)requestChannelsList;

@end
