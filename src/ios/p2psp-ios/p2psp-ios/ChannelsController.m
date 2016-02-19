//
//  ChannelsController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 19/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "ChannelsController.h"

@implementation ChannelsController

/**
 *  Callback called when the assocciated view is loaded
 */
- (void)viewDidLoad {
  self.channelsList = [[NSMutableArray alloc] init];

  [self.channelsList addObject:[[Channel alloc] init:@"Big Buck Bunny"
                                              withIP:@"127.0.0.1"
                                            withPort:@"4552"]];
}

/**
 *  The number of elements in data model
 *
 *  @param tableView The table view IBOutlet
 *  @param section   The section of the table
 *
 *  @return The number of elements
 */
- (NSInteger)tableView:(UITableView *)tableView
 numberOfRowsInSection:(NSInteger)section {
  return [self.channelsList count];
}

/**
 *  Render the table view controller with the data model
 *
 *  @param tableView The table view IBOutlet
 *  @param indexPath The index of the cell for row
 *
 *  @return The cell
 */
- (UITableViewCell *)tableView:(UITableView *)tableView
         cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  static NSString *reuseIdentifier = @"ChannelCell";

  UITableViewCell *cell =
      [tableView dequeueReusableCellWithIdentifier:reuseIdentifier];

  if (cell == nil) {
    cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                  reuseIdentifier:reuseIdentifier];
  }

  cell.textLabel.text = [[self.channelsList objectAtIndex:indexPath.row] title];

  NSString *ip = [[self.channelsList objectAtIndex:indexPath.row] ip];
  NSString *port = [[self.channelsList objectAtIndex:indexPath.row] port];
  NSString *address = [NSString stringWithFormat:@"%@%@%@", ip, @":", port];
  ;

  cell.detailTextLabel.text = address;

  return cell;
};

- (IBAction)onGetChannels:(id)sender {
  [self.channelsList
      addObject:[[Channel alloc]
                        init:[NSString
                                 stringWithFormat:@"%@%lu", @"Example",
                                                  [self.channelsList count]]
                      withIP:@"127.0.0.1"
                    withPort:@"4552"]];

  [self.tvChannelsList reloadData];
}
@end
