import {
  Dropdown,
  DropdownButton,
  DropdownMenu,
  DropdownItem,
  DropdownLabel,
  DropdownDivider,
} from "@/shared/dropdown";
import {
  Sidebar,
  SidebarHeader,
  SidebarItem,
  SidebarLabel,
  SidebarSection,
  SidebarBody,
  SidebarSpacer,
  SidebarFooter,
} from "@/shared/sidebar";
import {
  ArrowRightStartOnRectangleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  Cog8ToothIcon,
  PlusIcon,
  UserIcon,
} from "@heroicons/react/16/solid";
import {
  Cog6ToothIcon,
  HomeIcon,
  InboxIcon,
  MagnifyingGlassIcon,
  MegaphoneIcon,
  ServerIcon,
  ExclamationTriangleIcon,
  Squares2X2Icon,
} from "@heroicons/react/20/solid";

export function SideBarScada() {
  return (
    <Sidebar>
      {/* HEADER: Project / Site */}
      <SidebarHeader>
        <Dropdown>
          <DropdownButton as={SidebarItem} className="mb-2.5">
            <SidebarLabel>SCADA Plant A</SidebarLabel>
            <ChevronDownIcon />
          </DropdownButton>
          <DropdownMenu className="min-w-64" anchor="bottom start">
            <DropdownItem href="/plants/1/settings">
              <Cog8ToothIcon />
              <DropdownLabel>Plant Settings</DropdownLabel>
            </DropdownItem>
            <DropdownDivider />
            <DropdownItem href="/plants/1">
              <DropdownLabel>SCADA Plant A</DropdownLabel>
            </DropdownItem>
            <DropdownItem href="/plants/2">
              <DropdownLabel>SCADA Plant B</DropdownLabel>
            </DropdownItem>
            <DropdownDivider />
            <DropdownItem href="/plants/create">
              <PlusIcon />
              <DropdownLabel>New Plant…</DropdownLabel>
            </DropdownItem>
          </DropdownMenu>
        </Dropdown>

        {/* SEARCH & COMMUNICATION */}
        <SidebarSection>
          <SidebarItem href="/search">
            <MagnifyingGlassIcon />
            <SidebarLabel>Search Devices</SidebarLabel>
          </SidebarItem>
          <SidebarItem href="/inbox">
            <InboxIcon />
            <SidebarLabel>Inbox</SidebarLabel>
          </SidebarItem>
        </SidebarSection>
      </SidebarHeader>

      {/* BODY: Monitoring & Operations */}
      <SidebarBody>
        <SidebarSection>
          <SidebarItem href="/dashboard">
            <HomeIcon />
            <SidebarLabel>Dashboard</SidebarLabel>
          </SidebarItem>
          <SidebarItem href="/devices">
            <ServerIcon />
            <SidebarLabel>Devices</SidebarLabel>
          </SidebarItem>
          <SidebarItem href="/topology">
            <Squares2X2Icon />
            <SidebarLabel>Network Map</SidebarLabel>
          </SidebarItem>
          <SidebarItem href="/events">
            <ExclamationTriangleIcon />
            <SidebarLabel>Alarms</SidebarLabel>
            {/* Badge example */}
            <span className="ml-auto inline-block rounded-full bg-red-600 px-2 py-0.5 text-xs font-semibold text-white">
              3
            </span>
          </SidebarItem>
          <SidebarItem href="/orders">
            <Cog6ToothIcon />
            <SidebarLabel>Commands</SidebarLabel>
          </SidebarItem>
          <SidebarItem href="/broadcasts">
            <MegaphoneIcon />
            <SidebarLabel>Notifications</SidebarLabel>
          </SidebarItem>
        </SidebarSection>

        <SidebarSpacer />

        {/* ADMIN / SETTINGS */}
        <SidebarSection>
          <SidebarItem href="/settings">
            <Cog6ToothIcon />
            <SidebarLabel>System Settings</SidebarLabel>
          </SidebarItem>
        </SidebarSection>
      </SidebarBody>

      {/* FOOTER: User Account */}
      <SidebarFooter>
        <Dropdown>
          <DropdownButton as={SidebarItem}>
            <span className="flex min-w-0 items-center gap-3">
              <span className="min-w-0">
                <span className="block truncate text-sm/5 font-medium text-white">
                  Guest Operator
                </span>
                <span className="block truncate text-xs/5 font-normal text-zinc-400">
                  guest@example.com
                </span>
              </span>
            </span>
            <ChevronUpIcon />
          </DropdownButton>
          <DropdownMenu className="min-w-64" anchor="top start">
            <DropdownItem href="/my-profile">
              <UserIcon />
              <DropdownLabel>My Profile</DropdownLabel>
            </DropdownItem>
            <DropdownItem href="/settings">
              <Cog8ToothIcon />
              <DropdownLabel>Settings</DropdownLabel>
            </DropdownItem>
            <DropdownDivider />
            <DropdownItem href="/">
              <ArrowRightStartOnRectangleIcon />
              <DropdownLabel>Sign Out</DropdownLabel>
            </DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </SidebarFooter>
    </Sidebar>
  );
}
