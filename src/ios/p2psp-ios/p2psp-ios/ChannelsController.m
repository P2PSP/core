//
//  ChannelsController.m
//  p2psp-ios
//
//  Created by Antonio Vicente Martín on 19/02/16.
//  Copyright © 2016 P2PSP. All rights reserved.
//

#import "ChannelsController.h"

@interface ChannelsController ()<UITableViewDataSource, UITableViewDelegate>

@property(nonatomic) NSArray<Channel *> *channelsList;
@property(nonatomic) Channel *selectedChannel;
@property(nonatomic) BocastClient *bocastClient;

@property(weak, nonatomic) IBOutlet UITableView *tvChannelsList;
@property(weak, nonatomic) IBOutlet UITextField *tfServerAddress;

@end

@implementation ChannelsController

/**
 *  Callback called when the assocciated view is loaded
 */
- (void)viewDidLoad {
  self.bocastClient = [[BocastClient alloc] initWithBocastClientDelegate:self];

  // Data model
  self.channelsList = [[NSMutableArray alloc] init];
}

- (void)viewWillAppear:(BOOL)animated {
  // Show navigation bar
  [self.navigationController setNavigationBarHidden:NO];
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

  cell.detailTextLabel.text = address;

  return cell;
};

/**
 *  Callback for getChannels button
 *
 *  @param sender The UIButton
 */
- (IBAction)onGetChannels:(id)sender {
  // TODO: Display loading icon
  NSString *address = self.tfServerAddress.text;
  NSString *url = [NSString
      stringWithFormat:@"%@%@%@", @"http://", address, @"/api/channels"];

  self.bocastClient.bocastURL = [NSURL URLWithString:url];
  [self.bocastClient requestChannelsList];
}

/**
 *  Prepare the data to pass to the next viewcontroller
 *
 *  @param segue  The segue reference
 *  @param sender The UIView sender
 */
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
  PlayerController *vcPlayerController =
      (PlayerController *)segue.destinationViewController;

  // Debug splitter segue
  if ([segue.identifier isEqual:@"debugSplitter"]) {
    self.selectedChannel = [[Channel alloc] init:@""
                                 withDescription:@""
                                          withIP:@"127.0.0.1"
                                        withPort:@"4552"];

    // Channel selected segue
  } else if ([segue.identifier isEqual:@"watchPlayerController"]) {
    UITableViewCell *cell = (UITableViewCell *)sender;
    NSIndexPath *indexPath = [self.tvChannelsList indexPathForCell:cell];
    long index = indexPath.row;
    self.selectedChannel = self.channelsList[index];
  }

  [vcPlayerController setChannel:self.selectedChannel];
}

/**
 *  This method is called when the stacked scene pops out the stack to this
 * scene
 *
 *  @param unwindSegue The storyboard segue
 */
- (IBAction)unwindToChannels:(UIStoryboardSegue *)unwindSegue {
}

/**
 *  Dissmiss keyboard
 *
 *  @param sender The sender of the IBAction
 */
- (IBAction)onKeyboardDismiss:(id)sender {
  [sender setCancelsTouchesInView:NO];
  [self.view endEditing:YES];
}

/**
 *  BocastClientDelegate - Shows an UIAlertView to display errors
 *
 *  @param error The error object
 */
- (void)onError:(NSError *)error {
  // TODO: Hide loading icon
  dispatch_async(dispatch_get_main_queue(), ^{
    UIAlertView *alert =
        [[UIAlertView alloc] initWithTitle:@"Error"
                                   message:[error localizedDescription]
                                  delegate:self
                         cancelButtonTitle:@"OK"
                         otherButtonTitles:nil];
    [alert show];
  });
}

/**
 *  BocastClientDelegate - Get the values of the channels obtained from the
 * server
 *
 *  @param channelsList The array of the channels
 */
- (void)onChannelsListSuccess:(NSArray<Channel *> *)channelsList {
  // TODO: Hide loading icon
  self.channelsList = channelsList;

  dispatch_async(dispatch_get_main_queue(), ^{
    [self.tvChannelsList reloadSections:[NSIndexSet indexSetWithIndex:0]
                       withRowAnimation:UITableViewRowAnimationFade];
  });
}

@end
