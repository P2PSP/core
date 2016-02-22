//
//  BocastClient.h
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 22/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "Channel.h"

@protocol BocastClientDelegate;

@interface BocastClient : NSObject

/**
 *  The url of the server
 */
@property(nonatomic) NSURL* bocastURL;
@property(nonatomic) id<BocastClientDelegate> bocastClientDelegate;

- (instancetype)initWithBocastClientDelegate:
    (id<BocastClientDelegate>)bocastClientDelegate;

/**
 *  Makes an http request to the server to get the channels list
 */
- (void)requestChannelsList;

@end

/**
 *  The purpose of this protocol is to be a handler for the view controller
 */
@protocol BocastClientDelegate<NSObject>

/**
 *  This callback will be called after a success channels list request
 *
 *  @param channelsList The array of channels
 */
- (void)onChannelsListSuccess:(NSArray<Channel*>*)channelsList;

/**
 *  This callback will be called after any process failure
 *
 *  @param error The error object
 */
- (void)onError:(NSError*)error;

@end