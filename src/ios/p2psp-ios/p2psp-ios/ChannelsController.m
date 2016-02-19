//
//  ChannelsController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 19/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "ChannelsController.h"

@interface ChannelsController ()<UITableViewDataSource, UITableViewDelegate>

@property(nonatomic) NSMutableArray<Channel *> *channelsList;
@property(nonatomic) Channel *selectedChannel;

@property(weak, nonatomic) IBOutlet UITableView *tvChannelsList;

@end

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

/**
 *  Callback for getChannels button
 *
 *  @param sender The UIButton
 */
- (IBAction)onGetChannels:(id)sender {
  [self.channelsList
      addObject:[[Channel alloc]
                        init:[NSString
                                 stringWithFormat:@"%@%lu", @"Example",
                                                  (unsigned long)
                                                      [self.channelsList count]]
                      withIP:@"127.0.0.2"
                    withPort:@"4553"]];

  [self.tvChannelsList reloadData];
}

/**
 *  Prepare the data to pass to the next viewcontroller
 *
 *  @param segue  The segue reference
 *  @param sender The UIView sender
 */
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
  if ([segue.identifier isEqual:@"watchPlayerController"]) {
    UITableViewCell *cell = (UITableViewCell *)sender;
    NSIndexPath *indexPath = [self.tvChannelsList indexPathForCell:cell];
    int index = indexPath.row;
    self.selectedChannel = self.channelsList[index];

    PlayerController *vcPlayerController =
        (PlayerController *)segue.destinationViewController;

    [vcPlayerController setChannel:self.selectedChannel];
  }
}

@end
