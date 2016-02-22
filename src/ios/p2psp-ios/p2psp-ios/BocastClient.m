//
//  BocastClient.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 22/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "BocastClient.h"

@implementation BocastClient

- (instancetype)initWithBocastClientDelegate:
    (id<BocastClientDelegate>)bocastClientDelegate {
  self = [super init];
  if (self) {
    self.bocastClientDelegate = bocastClientDelegate;
  }
  return self;
}

/**
 *  Makes an http request to the server to get the channels list
 */
- (void)requestChannelsList {
  NSURLRequest *urlRequest = [[NSURLRequest alloc] initWithURL:self.bocastURL];

  [NSURLConnection sendAsynchronousRequest:urlRequest
                                     queue:[[NSOperationQueue alloc] init]
                         completionHandler:^(NSURLResponse *response,
                                             NSData *data, NSError *error) {

                           if (error) {
                             [self hanldeError:error];
                           } else {
                             [self getChannelsList:data];
                           }
                         }];
}

/**
 *  Builds the objects in memory for the received JSON
 *
 *  @param data The JSON data
 */
- (void)getChannelsList:(NSData *)data {
  NSError *localError = nil;
  NSArray *parsedObject =
      [NSJSONSerialization JSONObjectWithData:data options:0 error:&localError];

  // Handle error within JSON
  if (localError != nil) {
    [self hanldeError:localError];
  }

  NSMutableArray *channelsList = [[NSMutableArray alloc] init];

  for (NSDictionary *jsonChannel in parsedObject) {
    Channel *channel = [[Channel alloc] init];

    // TODO: Find a way to automate this
    if ([channel respondsToSelector:NSSelectorFromString(@"title")]) {
      channel.title = [jsonChannel valueForKey:@"title"];
    }

    if ([channel respondsToSelector:NSSelectorFromString(@"desc")]) {
      channel.desc = [jsonChannel valueForKey:@"desc"];
    }

    if ([channel respondsToSelector:NSSelectorFromString(@"ip")]) {
      channel.ip = [jsonChannel valueForKey:@"ip"];
    }

    if ([channel respondsToSelector:NSSelectorFromString(@"port")]) {
      channel.port = [jsonChannel valueForKey:@"port"];
    }

    [channelsList addObject:channel];
  }

  [self.bocastClientDelegate
      onChannelsListSuccess:[[NSArray<Channel *> alloc]
                                initWithArray:channelsList]];
}

/**
 *  Handles the errors of the server connections
 *
 *  @param error The error object
 */
- (void)hanldeError:(NSError *)error {
  [self.bocastClientDelegate onError:error];
}

@end
