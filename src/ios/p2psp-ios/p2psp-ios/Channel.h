//
//  Channel.h
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 19/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface Channel : NSObject

@property(nonatomic) NSString* title;
@property(nonatomic) NSString* desc;
@property(nonatomic) NSString* ip;
@property(nonatomic) NSString* port;

- (instancetype)init:(NSString*)title
     withDescription:(NSString*)description
              withIP:(NSString*)ip
            withPort:(NSString*)port;

@end
